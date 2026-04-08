#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <chrono>
#include <sstream>
#include <cstdlib>

class CmdVelToG1 : public rclcpp::Node
{
public:
    CmdVelToG1() : Node("cmd_vel_to_g1")
    {
        // Declare parameters
        this->declare_parameter<std::string>("network_interface", "enx00051bd51a1a");
        this->declare_parameter<std::string>("g1_loco_client_path", "/home/rey/unitree_g1_control/unitree_sdk2/build/bin/g1_loco_client");
        this->declare_parameter<double>("command_timeout", 0.1); // seconds
        this->declare_parameter<double>("max_x_linear_velocity", 0.2); // m/s
        this->declare_parameter<double>("max_y_linear_velocity", 0.15); // m/s
        this->declare_parameter<double>("max_angular_velocity", 0.2); // rad/s
        
        // Get parameters
        this->get_parameter("network_interface", network_interface_);
        this->get_parameter("g1_loco_client_path", g1_loco_client_path_);
        this->get_parameter("command_timeout", command_timeout_);
        this->get_parameter("max_x_linear_velocity", max_x_linear_vel_);
        this->get_parameter("max_y_linear_velocity", max_y_linear_vel_);
        this->get_parameter("max_angular_velocity", max_angular_vel_);
        
        // Create subscriber
        cmd_vel_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "cmd_vel", 10,
            std::bind(&CmdVelToG1::cmdVelCallback, this, std::placeholders::_1));
        
        RCLCPP_INFO(this->get_logger(), "G1 cmd_vel bridge node started");
        RCLCPP_INFO(this->get_logger(), "Network interface: %s", network_interface_.c_str());
        RCLCPP_INFO(this->get_logger(), "G1 loco client path: %s", g1_loco_client_path_.c_str());
        RCLCPP_INFO(this->get_logger(), "Command timeout: %.2f seconds", command_timeout_);
        RCLCPP_INFO(this->get_logger(), "Max X linear velocity: %.2f m/s", max_x_linear_vel_);
        RCLCPP_INFO(this->get_logger(), "Max Y linear velocity: %.2f m/s", max_y_linear_vel_);
        RCLCPP_INFO(this->get_logger(), "Max angular velocity: %.2f rad/s", max_angular_vel_);
        RCLCPP_INFO(this->get_logger(), "Listening to /cmd_vel...");
    }

private:
    double clamp(double value, double max_abs)
    {
        if (value > max_abs) return max_abs;
        if (value < -max_abs) return -max_abs;
        return value;
    }

    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg)
    {
        auto current_time = this->now();
        
        // Check if enough time has passed since last command (safety debouncing)
        if ((current_time - last_command_time_).seconds() < command_timeout_)
        {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                "Command rate too high, skipping command for safety");
            return;
        }
        
        // Extract and clamp velocity values for safety
        double linear_x = clamp(msg->linear.x, max_x_linear_vel_);
        double linear_y = clamp(msg->linear.y, max_y_linear_vel_);
        double angular_z = clamp(msg->angular.z, max_angular_vel_);
        
        // Log if velocities were clamped
        if (std::abs(msg->linear.x) > max_x_linear_vel_ ||
            std::abs(msg->linear.y) > max_y_linear_vel_ ||
            std::abs(msg->angular.z) > max_angular_vel_)
        {
            RCLCPP_WARN(this->get_logger(), 
                "Velocity clamped for safety! Requested: [%.2f, %.2f, %.2f] -> Clamped: [%.2f, %.2f, %.2f]",
                msg->linear.x, msg->linear.y, msg->angular.z,
                linear_x, linear_y, angular_z);
        }
        
        // Build the command string
        std::ostringstream move_values;
        move_values << linear_x << " " << linear_y << " " << angular_z;
        
        std::ostringstream command;
        command << g1_loco_client_path_
                << " --network_interface=" << network_interface_
                << " --move=\"" << move_values.str() << "\"";
        
        RCLCPP_INFO(this->get_logger(), "Executing: %s", command.str().c_str());
        
        // Execute the command
        int result = std::system(command.str().c_str());
        
        if (result == 0)
        {
            RCLCPP_INFO(this->get_logger(), "Command executed successfully: linear_x=%.2f, linear_y=%.2f, angular_z=%.2f",
                        linear_x, linear_y, angular_z);
        }
        else
        {
            RCLCPP_ERROR(this->get_logger(), "Command execution failed with code: %d", result);
        }
        
        // Update last command time
        last_command_time_ = current_time;
    }

    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
    std::string network_interface_;
    std::string g1_loco_client_path_;
    double command_timeout_;
    double max_x_linear_vel_;
    double max_y_linear_vel_;
    double max_angular_vel_;
    rclcpp::Time last_command_time_{0, 0, RCL_ROS_TIME};
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    
    try
    {
        auto node = std::make_shared<CmdVelToG1>();
        rclcpp::spin(node);
    }
    catch (const std::exception& e)
    {
        RCLCPP_ERROR(rclcpp::get_logger("cmd_vel_to_g1"), "Exception caught: %s", e.what());
    }
    
    rclcpp::shutdown();
    return 0;
}

#include <chrono>
#include <iostream>
#include <thread>
#include <vector>
#include <utility>

#include <unitree/robot/g1/loco/g1_loco_api.hpp>
#include <unitree/robot/g1/loco/g1_loco_client.hpp>

std::vector<float> stringToFloatVector(const std::string &str) {
  std::vector<float> result;
  std::stringstream ss(str);
  float num;
  while (ss >> num) {
    result.push_back(num);
    ss.ignore();
  }
  return result;
}

int main(int argc, char const *argv[]) {
  std::string network_interface = "lo";
  std::vector<std::pair<std::string, std::string>> commands;

  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if (arg.substr(0, 2) == "--") {
      size_t pos = arg.find("=");
      std::string key, value;
      if (pos != std::string::npos) {
        key = arg.substr(2, pos - 2);
        value = arg.substr(pos + 1);
        if (value.front() == '"' && value.back() == '"') {
          value = value.substr(1, value.length() - 2);
        }
      } else {
        key = arg.substr(2);
        value = "";
      }
      if (key == "network_interface") {
        network_interface = value;
      } else {
        commands.push_back({key, value});
      }
    }
  }

  unitree::robot::ChannelFactory::Instance()->Init(0, network_interface);

  unitree::robot::g1::LocoClient client;
  client.Init();
  client.SetTimeout(10.f);

  for (const auto &arg_pair : commands) {
    std::cout << "Processing command: [" << arg_pair.first << "] with param: ["
              << arg_pair.second << "] ..." << std::endl;

    if (arg_pair.first == "get_fsm_id") {
      int fsm_id;
      client.GetFsmId(fsm_id);
      std::cout << "current fsm_id: " << fsm_id << std::endl;
    }
    if (arg_pair.first == "get_fsm_mode") {
      int fsm_mode;
      client.GetFsmMode(fsm_mode);
      std::cout << "current fsm_mode: " << fsm_mode << std::endl;
    }
    if (arg_pair.first == "switch_move_mode") {
      bool flag = (arg_pair.second == "true");
      client.SwitchMoveMode(flag);
    }
    if (arg_pair.first == "move") {
      std::vector<float> param = stringToFloatVector(arg_pair.second);
      if (param.size() == 3) {
        client.Move(param[0], param[1], param[2]);
      }
    }
    if (arg_pair.first == "set_velocity") {
      std::vector<float> param = stringToFloatVector(arg_pair.second);
      if (param.size() >= 3) {
        float duration = (param.size() >= 4) ? param[3] : 1.0f;
        client.SetVelocity(param[0], param[1], param[2], duration);
        std::cout << "set velocity to " << param[0] << " " << param[1] << " " << param[2] << " " << duration << std::endl;
      }
    }
    if (arg_pair.first == "stop_move") {
      client.StopMove();
    }
    if (arg_pair.first == "stand_up") {
      client.StandUp();
    }
    if (arg_pair.first == "start") {
      client.Start();
    }
    if (arg_pair.first == "damp") {
      client.Damp();
    }
    std::cout << "Done!" << std::endl;
  }

  return 0;
}

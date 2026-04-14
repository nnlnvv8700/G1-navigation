#include <chrono>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>

#include <unitree/idl/hg/LowState_.hpp>
#include <unitree/robot/channel/channel_subscriber.hpp>
#include <unitree/robot/g1/loco/g1_loco_client.hpp>

namespace {

struct Args {
  std::string network_interface;
  int wait_ms = 3000;
};

Args ParseArgs(int argc, char const* argv[]) {
  Args args;

  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if (arg == "--help" || arg == "-h") {
      std::cout
          << "Usage: " << argv[0]
          << " [--network_interface=<iface>] [--wait_ms=<ms>]\n"
          << "  --network_interface : DDS network interface, e.g. enp108s0\n"
          << "  --wait_ms           : wait timeout for lowstate and RPC checks\n";
      std::exit(0);
    }

    if (arg.rfind("--network_interface=", 0) == 0) {
      args.network_interface = arg.substr(std::strlen("--network_interface="));
      continue;
    }

    if (arg.rfind("--wait_ms=", 0) == 0) {
      args.wait_ms = std::stoi(arg.substr(std::strlen("--wait_ms=")));
      continue;
    }

    std::cerr << "Unknown argument: " << arg << "\n";
    std::exit(1);
  }

  return args;
}

void PrintRet(const std::string& label, int32_t ret) {
  std::cout << label << ": ret=" << ret << "\n";
}

}  // namespace

int main(int argc, char const* argv[]) {
  const Args args = ParseArgs(argc, argv);

  std::cout << "=== G1 SDK Smoke Test ===\n";
  if (args.network_interface.empty()) {
    std::cout << "network_interface: <auto>\n";
    std::cout << "hint: if discovery fails, rerun with "
                 "--network_interface=<your_ethernet_iface>\n";
  } else {
    std::cout << "network_interface: " << args.network_interface << "\n";
  }
  std::cout << "wait_ms: " << args.wait_ms << "\n";

  unitree::robot::ChannelFactory::Instance()->Init(0, args.network_interface);

  std::mutex lowstate_mutex;
  bool got_lowstate = false;
  unitree_hg::msg::dds_::LowState_ latest_lowstate;

  auto lowstate_subscriber =
      std::make_shared<
          unitree::robot::ChannelSubscriber<unitree_hg::msg::dds_::LowState_>>(
          "rt/lowstate");
  lowstate_subscriber->InitChannel(
      [&](const void* message) {
        std::lock_guard<std::mutex> lock(lowstate_mutex);
        latest_lowstate =
            *static_cast<const unitree_hg::msg::dds_::LowState_*>(message);
        got_lowstate = true;
      },
      1);

  const auto deadline =
      std::chrono::steady_clock::now() + std::chrono::milliseconds(args.wait_ms);
  while (std::chrono::steady_clock::now() < deadline) {
    {
      std::lock_guard<std::mutex> lock(lowstate_mutex);
      if (got_lowstate) {
        break;
      }
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
  }

  bool lowstate_ok = false;
  {
    std::lock_guard<std::mutex> lock(lowstate_mutex);
    lowstate_ok = got_lowstate;
    if (lowstate_ok) {
      const auto& rpy = latest_lowstate.imu_state().rpy();
      std::cout << "lowstate: OK"
                << " tick=" << latest_lowstate.tick()
                << " mode_machine=" << static_cast<int>(latest_lowstate.mode_machine())
                << " rpy=(" << rpy[0] << ", " << rpy[1] << ", " << rpy[2] << ")"
                << " motor0.q=" << latest_lowstate.motor_state().at(0).q() << "\n";
    } else {
      std::cout << "lowstate: TIMEOUT after " << args.wait_ms << " ms\n";
    }
  }

  unitree::robot::g1::LocoClient client;
  client.Init();
  client.SetTimeout(static_cast<float>(args.wait_ms) / 1000.0f);

  bool loco_ok = true;

  int fsm_id = -1;
  int32_t ret = client.GetFsmId(fsm_id);
  PrintRet("GetFsmId", ret);
  loco_ok = loco_ok && (ret == 0);
  if (ret == 0) {
    std::cout << "  value=" << fsm_id << "\n";
  }

  int fsm_mode = -1;
  ret = client.GetFsmMode(fsm_mode);
  PrintRet("GetFsmMode", ret);
  loco_ok = loco_ok && (ret == 0);
  if (ret == 0) {
    std::cout << "  value=" << fsm_mode << "\n";
  }

  int balance_mode = -1;
  ret = client.GetBalanceMode(balance_mode);
  PrintRet("GetBalanceMode", ret);
  loco_ok = loco_ok && (ret == 0);
  if (ret == 0) {
    std::cout << "  value=" << balance_mode << "\n";
  }

  float swing_height = 0.0f;
  ret = client.GetSwingHeight(swing_height);
  PrintRet("GetSwingHeight", ret);
  loco_ok = loco_ok && (ret == 0);
  if (ret == 0) {
    std::cout << "  value=" << swing_height << "\n";
  }

  float stand_height = 0.0f;
  ret = client.GetStandHeight(stand_height);
  PrintRet("GetStandHeight", ret);
  loco_ok = loco_ok && (ret == 0);
  if (ret == 0) {
    std::cout << "  value=" << stand_height << "\n";
  }

  std::cout << "\nSummary:\n";
  std::cout << "  DDS lowstate subscription: " << (lowstate_ok ? "OK" : "FAIL") << "\n";
  std::cout << "  LocoClient read-only RPCs: " << (loco_ok ? "OK" : "FAIL") << "\n";

  if (lowstate_ok && loco_ok) {
    std::cout << "Smoke test passed.\n";
    return 0;
  }

  std::cout << "Smoke test failed.\n";
  return 1;
}

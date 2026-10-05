#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include "json.hpp"

using json = nlohmann::json;

struct Process {
    std::string pid;
    int arrival;
    int burst;
    int completion = 0;
    int turnaround = 0;
    int waiting = 0;
};

int main() {
    std::ifstream inFile("../data/input.json");
    if (!inFile) {
        std::cerr << "Error: Cannot open input.json\n";
        return 1;
    }

    json input;
    try {
        inFile >> input;
    } catch (const std::exception& e) {
        std::cerr << "JSON parse error: " << e.what() << '\n';
        return 1;
    }

    std::vector<Process> processes;
    for (const auto& p : input["processes"]) {
        processes.push_back({p.at("pid"), p.at("arrival"), p.at("burst")});
    }

    std::stable_sort(processes.begin(), processes.end(),
        [](const Process& a, const Process& b) {
            return a.arrival < b.arrival;
        });

    const int n = static_cast<int>(processes.size());
    int time = 0;
    std::vector<std::string> gantt;

    for (auto& p : processes) {
        if (time < p.arrival) {
            while (time < p.arrival) {
                gantt.push_back("idle");
                ++time;
            }
        }

        for (int t = 0; t < p.burst; ++t) {
            gantt.push_back(p.pid);
            ++time;
        }

        p.completion = time;
        p.turnaround = p.completion - p.arrival;
        p.waiting = p.turnaround - p.burst;
    }

    json output;
    output["gantt_chart"] = gantt;
    output["results"] = json::array();

    double totalWaiting = 0.0;
    double totalTurnaround = 0.0;

    for (const auto& p : processes) {
        output["results"].push_back({
            {"pid", p.pid},
            {"arrival", p.arrival},
            {"burst", p.burst},
            {"completion", p.completion},
            {"turnaround", p.turnaround},
            {"waiting", p.waiting}
        });
        totalWaiting += p.waiting;
        totalTurnaround += p.turnaround;
    }

    output["average_waiting"] = n ? totalWaiting / n : 0.0;
    output["average_turnaround"] = n ? totalTurnaround / n : 0.0;

    std::ofstream outFile("../data/output.json");
    if (!outFile) {
        std::cerr << "Error: Cannot write output.json\n";
        return 1;
    }

    outFile << output.dump(2);
    std::cout << "FCFS scheduling complete.\n";
    return 0;
}

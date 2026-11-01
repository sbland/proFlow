"""Build a process network with indexed, keyed, and unresolved state inputs."""

from proflow.analysis.network.extract_nodes_and_edges import processes_to_nodes_and_edges
from proflow.helpers import lget
from proflow.objects.interface import I
from proflow.objects.process import Process


def collect_weather():
    return None


def summarize_weather(first_reading, latest_reading, station, elevation):
    return first_reading, latest_reading, station, elevation


def correct_summary(summary):
    return summary


def publish_report(summary, middle_reading):
    return summary, middle_reading


def build_processes() -> list[Process]:
    return [
        Process(
            func=collect_weather,
            comment="Collect indexed readings and station metadata",
            state_outputs=lambda result: [
                (result["readings"][0], "weather.readings[0]"),
                (result["readings"][1], "weather.readings[1]"),
                (result["readings"][-1], "weather.readings[-1]"),
                (result["station"], "weather.station"),
            ],
        ),
        Process(
            func=summarize_weather,
            comment="Read indexed values and a dictionary key",
            state_inputs=lambda state: [
                I(lget(state.weather.readings, 0, "missing"), as_="first_reading"),
                I(state.weather.readings[-1], as_="latest_reading"),
                I(state.weather["station"], as_="station"),
                I(state.location["elevation"], as_="elevation"),
            ],
            state_outputs=lambda result: [
                (result, "daily.summary"),
            ],
        ),
        Process(
            func=correct_summary,
            comment="Overwrite the summary with a corrected value",
            state_inputs=lambda state: [
                I(state.daily.summary, as_="summary"),
            ],
            state_outputs=lambda result: [
                (result, "daily.summary"),
            ],
        ),
        Process(
            func=publish_report,
            comment="Use the newest summary and another indexed reading",
            state_inputs=lambda state: [
                I(state.daily.summary, as_="summary"),
                I(state.weather.readings[1], as_="middle_reading"),
            ],
            state_outputs=lambda result: [
                (result, "daily.report"),
            ],
        ),
    ]


def main() -> None:
    nodes, edges = processes_to_nodes_and_edges(build_processes())
    print("Nodes:")
    for node in nodes:
        print(f"  {node.index}: {node.text}")

    print("Edges (producer -> consumer):")
    for edge in edges:
        if edge.target == -1:
            print(f"  unresolved: {edge.name} -> process {edge.source}")
        else:
            print(f"  process {edge.target} -> {edge.name} -> process {edge.source}")


if __name__ == "__main__":
    main()

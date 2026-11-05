/** Fetch the exported graph and initialize the process network webview. */
import "./style.css";
import { fetchGraphData } from "./graph-data";
import { renderGraph } from "./graph";

/** Load the graph and display failures in the accessible alert region. */
async function startWebview(): Promise<void> {
  try {
    renderGraph(await fetchGraphData());
  } catch (error) {
    const alert = document.querySelector<HTMLElement>("#webview-error");
    const message =
      error instanceof Error ? error.message : "An unknown error occurred.";
    console.error("Unable to load process graph:", error);
    if (alert) {
      alert.textContent = `Unable to load process graph: ${message}`;
      alert.hidden = false;
    }
  }
}

void startWebview();

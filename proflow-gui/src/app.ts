/* force directed graph with direction arrows and multiple edges

References

http://jsfiddle.net/zhanghuancs/a2QpA/
https://bl.ocks.org/mattkohl/146d301c0fc20d89d85880df537de7b0
http://bl.ocks.org/fancellu/2c782394602a93921faff74e594d1bb1
*/

// const { sortLinks, setLinkIndexAndNum } = require("./utils");
// const { arcPath } = require("./draw");

import * as d3 from "d3";
import { sortLinks, setLinkIndexAndNum } from "./utils";
import { arcPath } from "./draw";

/* Globals */

var colors = d3.scaleOrdinal(d3.schemeCategory10);

var svg = d3.select("svg");
var width = +svg.attr("width");
var height = +svg.attr("height");

/* Generate svg */
svg
  .append("defs")
  .append("marker")
  .attrs({
    id: "arrowhead",
    viewBox: "-0 -5 10 10",
    refX: 13,
    refY: 0,
    orient: "auto",
    markerWidth: 13,
    markerHeight: 13,
    xoverflow: "visible",
  })
  .append("svg:path")
  .attr("d", "M 0,-5 L 10 ,0 L 0,5")
  .attr("fill", "#999")
  .style("stroke", "none");

var simulation = d3
  .forceSimulation()
  .force(
    "link",
    d3
      .forceLink()
      .id(function (d) {
        return d.id;
      })
      .distance(500)
      .strength(0.5)
  )
  .force("charge", d3.forceManyBody())
  .force("center", d3.forceCenter(width / 2, height / 2));

/* load data */
d3.json("/data/force.json", function (error, graph) {
  if (error) throw error;
  var linksData = graph.links;
  sortLinks(linksData);
  var mLinkNum = setLinkIndexAndNum(linksData);
  update(linksData, graph.nodes, mLinkNum);
});

/* Assign data to d3 svg */
function update(links, nodes, mLinkNum: { [k: string]: number } = {}) {
  var link;
  var pathInvis;
  var node;
  link = svg
    .selectAll(".link")
    .data(links)
    .enter()
    // .append("line")
    .append("svg:path")
    .attr("class", "link")
    .attr("marker-end", "url(#arrowhead)");

  link.append("title").text(function (d) {
    return d.name;
  });

  pathInvis = svg
    .selectAll(".pathInvis")
    .data(links)
    .enter()
    // .append("line")
    .append("svg:path")
    .attr("id", function (d) {
      return "invis_" + d.source + "-" + d.linkindex + "-" + d.target;
    })
    .attr("class", "pathInvis");

  var pathLabel = svg
    .selectAll(".pathLabel")
    .data(links)
    .enter()
    // .append("g")
    .append("svg:text")
    .attr("class", "pathLabel")
    .attr("text-anchor", "middle")
    .append("svg:textPath")
    .attr("startOffset", "50%")
    .attr("xlink:href", function (d) {
      return "#invis_" + d.source + "-" + d.linkindex + "-" + d.target;
    })
    .style("fill", "#cccccc")
    .style("font-size", 30)
    .text(function (d) {
      return d.name;
    });
  node = svg
    .selectAll(".node")
    .data(nodes)
    .enter()
    .append("g")
    .attr("class", "node")
    .call(d3.drag().on("start", dragstarted).on("drag", dragged));

  node
    .append("circle")
    .attr("r", 5)
    .style("fill", function (d, i) {
      return colors(i);
    });

  node.append("title").text(function (d) {
    return d.id;
  });

  node
    .append("text")
    .attr("dy", -3)
    .text(function (d) {
      return d.name + ":" + d.text;
    });

  simulation
    .nodes(nodes)
    .on("tick", ticked(link, pathInvis, node, mLinkNum, nodes));

  simulation.force("link").links(links);
}

const ticked = (link, pathInvis, node, mLinkNum, nodes) =>
  function tickedInner() {
    link.attr("d", function (d) {
      return arcPath(mLinkNum, true, d, nodes);
    });

    pathInvis.attr("d", function (d) {
      // const source = nodes[d.source];
      // const target = nodes[d.target];

      const source = d.source;
      const target = d.target;
      return arcPath(mLinkNum, source.x < target.x, d, nodes);
    });

    node.attr("transform", function (d) {
      return "translate(" + d.x + ", " + d.y + ")";
    });
  };

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.02).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

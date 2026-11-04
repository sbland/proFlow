/* force directed graph with direction arrows and multiple edges

References

http://jsfiddle.net/zhanghuancs/a2QpA/
https://bl.ocks.org/mattkohl/146d301c0fc20d89d85880df537de7b0
http://bl.ocks.org/fancellu/2c782394602a93921faff74e594d1bb1
*/

var NODE_WIDTH = 180,
    NODE_HEIGHT = 48,
    NODE_DOT_RADIUS = 5,
    currentNodeShape = "box";

function sortLinks(lks) {
    lks.sort(function (a, b) {
        if (a.source > b.source) {
            return 1;
        }
        else if (a.source < b.source) {
            return -1;
        }
        else {
            if (a.target > b.target) {
                return 1;
            }
            if (a.target < b.target) {
                return -1;
            }
            else {
                return 0;
            }
        }
    });
}

var mLinkNum = {};
function setLinkIndexAndNum(linksData) {
    //any links with duplicate source and target get an incremented 'linknum'
    for (var i = 0; i < linksData.length; i++) {
        if (i != 0 &&
            linksData[i].source == linksData[i - 1].source &&
            linksData[i].target == linksData[i - 1].target) {
            linksData[i].linkindex = linksData[i - 1].linkindex + 1;
        }
        else {
            linksData[i].linkindex = 1;
        }
        // save the total number of links between two nodes
        if (mLinkNum[linksData[i].target + "," + linksData[i].source] !== undefined) {
            mLinkNum[linksData[i].target + "," + linksData[i].source] = linksData[i].linkindex;
        }
        else {
            mLinkNum[linksData[i].source + "," + linksData[i].target] = linksData[i].linkindex;
        }
    }
}

var getSiblingLinks = function (source, target) {
    var siblings = [];
    for (var i = 0; i < mLinkNum.length; ++i) {
        if ((mLinkNum[i].source == source && mLinkNum[i].target == target) || (mLinkNum[i].source == target && mLinkNum[i].target == source))
            siblings.push(mLinkNum[i].id);
    };
    return siblings;
};
/**
 * Get source and target edge coordinates for the currently selected node shape.
 */
function nodeBoundaryPoints(d) {
    var dx = d.target.x - d.source.x,
        dy = d.target.y - d.source.y,
        distance = Math.sqrt(dx * dx + dy * dy);

    if (currentNodeShape === "dot") {
        var offset = distance ? NODE_DOT_RADIUS / distance : 0;
        return {
            source: {
                x: d.source.x + dx * offset,
                y: d.source.y + dy * offset
            },
            target: {
                x: d.target.x - dx * offset,
                y: d.target.y - dy * offset
            }
        };
    }

    return {
        source: { x: d.source.x + NODE_WIDTH / 2, y: d.source.y },
        target: { x: d.target.x - NODE_WIDTH / 2, y: d.target.y }
    };
}

/**
 * Build a Bézier link with endpoint tangents matching the selected node shape.
 * @param {boolean} leftHand Whether to draw from the source toward the target.
 * @param {Object} d The graph link datum containing source and target nodes.
 * @returns {string} SVG path data for the link.
 */
function bezierPath(leftHand, d) {
    var endpoints = nodeBoundaryPoints(d),
        start = leftHand ? endpoints.source : endpoints.target,
        end = leftHand ? endpoints.target : endpoints.source,
        startNode = leftHand ? d.source : d.target,
        endNode = leftHand ? d.target : d.source,
        dx = endNode.x - startNode.x,
        dy = endNode.y - startNode.y,
        distance = Math.sqrt(dx * dx + dy * dy) || 1,
        controlDistance = Math.max(NODE_WIDTH / 2, Math.abs(dx) / 2) +
            (d.linkindex - 1) * 12,
        control1,
        control2;

    if (currentNodeShape === "box") {
        var direction = leftHand ? 1 : -1;
        control1 = { x: start.x + direction * controlDistance, y: start.y };
        control2 = { x: end.x - direction * controlDistance, y: end.y };
    } else {
        var unitX = dx / distance,
            unitY = dy / distance;
        control1 = {
            x: start.x + unitX * controlDistance,
            y: start.y + unitY * controlDistance
        };
        control2 = {
            x: end.x - unitX * controlDistance,
            y: end.y - unitY * controlDistance
        };
    }

    return "M" + start.x + "," + start.y +
        "C" + control1.x + "," + control1.y +
        " " + control2.x + "," + control2.y +
        " " + end.x + "," + end.y;
}

var colors = d3.scaleOrdinal(d3.schemeCategory10);

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height"),
    graph,
    zoom,
    node,
    link,
    pathInvis,
    pathLabel;

var nodeFilter = d3.select("#node-filter"),
    nodeShapeControl = d3.selectAll('input[name="node-shape"]'),
    forceControl = d3.select("#forces-toggle"),
    forcesEnabled = forceControl.property("checked"),
    filterSummary = d3.select("#filter-summary"),
    totalNodeCount = 0;

svg.append('defs')
    .append('marker')
    .attrs({
        'id': 'arrowhead',
        'viewBox': '-0 -5 10 10',
        'refX': 13,
        'refY': 0,
        'orient': 'auto',
        'markerWidth': 13,
        'markerHeight': 13,
        'xoverflow': 'visible'
    })
    .append('svg:path')
    .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
    .attr('fill', '#999')
    .style('stroke', 'none');

graph = svg.append("g").attr("class", "graph-content");
zoom = d3.zoom()
    .scaleExtent([0.2, 4])
    .filter(function () {
        var event = d3.event,
            startsNodeDrag = (event.type === "mousedown" || event.type === "touchstart") &&
                event.target.closest(".node");
        return !event.button && (!event.ctrlKey || event.type === "wheel") && !startsNodeDrag;
    })
    .on("zoom", zoomed);
svg.call(zoom);

d3.select("#zoom-in").on("click", function () { zoomBy(1.2); });
d3.select("#zoom-out").on("click", function () { zoomBy(1 / 1.2); });
d3.select("#zoom-reset").on("click", resetZoom);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) { return d.id; }).distance(500).strength(0.5))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));


d3.json("/data", function (error, graph) {
    // d3.json("force/force.json", function (error, graph) {
    if (error) throw error;
    var linksData = graph.links
    sortLinks(linksData)
    setLinkIndexAndNum(linksData)
    update(linksData, graph.nodes);
});

function update(links, nodes) {
    totalNodeCount = nodes.length;

    link = graph.selectAll(".link")
        .data(links)
        .enter()
        // .append("line")
        .append("svg:path")
        .attr("class", "link")
        .attr('marker-end', 'url(#arrowhead)')

    link.append("title")
        .text(function (d) { return d.name; });

    pathInvis = graph.selectAll(".pathInvis")
        .data(links)
        .enter()
        // .append("line")
        .append("svg:path")
        .attr("id", function (d) {
            return 'invis_' + d.source + "-" + d.linkindex + "-" + d.target;
        })
        .attr("class", "pathInvis")

    pathLabel = graph.selectAll(".pathLabel")
        .data(links)
        .enter()
        // .append("g")
        .append("svg:text")
        .attr("class", "pathLabel")
        .attr("text-anchor", "middle")
        .append("svg:textPath")
        .attr("startOffset", "50%")
        .attr("xlink:href", function (d) {
            return '#invis_' + d.source + "-" + d.linkindex + "-" + d.target;;
        })
        .style("fill", "#cccccc")
        .style("font-size", 10)
        .text(function (d) { return d.name; });
    node = graph.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            //.on("end", dragended)
        );

    node.append("title")
        .text(function (d) { return d.id; });

    node.append("text")
        .text(function (d) { return d.name + ":" + d.text; });

    simulation
        .nodes(nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(links);

    nodeShapeControl.on("change", renderNodeShape);
    renderNodeShape();
    nodeFilter.on("input", applyNodeFilter);
    applyNodeFilter();
    forceControl.on("change", toggleForces);
}

/** Apply D3's current zoom transform to all graph elements together. */
function zoomed() {
    graph.attr("transform", d3.event.transform);
}

/** Adjust zoom from a control button while keeping the viewport center fixed. */
function zoomBy(factor) {
    svg.call(zoom.scaleBy, factor);
}

/** Restore the graph's original, unzoomed view. */
function resetZoom() {
    svg.call(zoom.transform, d3.zoomIdentity);
}

/** Render the selected node shape and redraw links to match its boundaries. */
/** Start or stop the graph layout simulation based on the force control. */
function toggleForces() {
    forcesEnabled = this.checked;
    if (forcesEnabled) {
        simulation.alpha(1).restart();
    } else {
        simulation.stop();
    }
}

function renderNodeShape() {
    currentNodeShape = nodeShapeControl
        .filter(function () { return this.checked; })
        .property("value");
    node.selectAll(".node-shape").remove();

    if (currentNodeShape === "box") {
        node.insert("rect", "title")
            .attr("class", "node-shape")
            .attr("x", -NODE_WIDTH / 2)
            .attr("y", -NODE_HEIGHT / 2)
            .attr("width", NODE_WIDTH)
            .attr("height", NODE_HEIGHT)
            .attr("rx", 4)
            .style("fill", function (d, i) { return colors(i); });
    } else {
        node.insert("circle", "title")
            .attr("class", "node-shape")
            .attr("r", NODE_DOT_RADIUS)
            .style("fill", function (d, i) { return colors(i); });
    }

    node.select("text")
        .attr("x", currentNodeShape === "box" ? 0 : NODE_DOT_RADIUS + 4)
        .attr("dy", currentNodeShape === "box" ? 4 : -3)
        .attr("text-anchor", currentNodeShape === "box" ? "middle" : "start");
    ticked();
}

/**
 * Show nodes matching the search and only links between visible nodes.
 */
function applyNodeFilter() {
    var query = nodeFilter.property("value").trim().toLowerCase();
    var visibleIds = new Set();

    node.each(function (d) {
        var matches = !query ||
            [d.id, d.name, d.text].join(" ").toLowerCase().includes(query);
        if (matches) {
            visibleIds.add(d.id);
        }
        d3.select(this).style("display", matches ? null : "none");
    });

    /** Return whether both endpoints are currently visible. */
    function linkIsVisible(d) {
        return visibleIds.has(d.source.id) && visibleIds.has(d.target.id);
    }

    link.style("display", function (d) {
        return linkIsVisible(d) ? null : "none";
    });
    pathInvis.style("display", function (d) {
        return linkIsVisible(d) ? null : "none";
    });
    pathLabel.style("display", function (d) {
        return linkIsVisible(d) ? null : "none";
    });
    filterSummary.text(visibleIds.size + " of " + totalNodeCount + " nodes shown");
}


function ticked() {
    link.attr("d", function (d) {
        return bezierPath(true, d);
    });

    pathInvis.attr("d", function (d) {
        return bezierPath(d.source.x < d.target.x, d);
    });

    node.attr("transform", function (d) { return "translate(" + d.x + ", " + d.y + ")"; });
}

/** Pin a node when dragging, restarting the layout only when forces are enabled. */
function dragstarted(d) {
    if (forcesEnabled && !d3.event.active) simulation.alphaTarget(0.02).restart()
    d.fx = d.x;
    d.fy = d.y;
}

/** Move a dragged node directly when the layout simulation is paused. */
function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
    if (!forcesEnabled) {
        d.x = d.fx;
        d.y = d.fy;
        ticked();
    }
}

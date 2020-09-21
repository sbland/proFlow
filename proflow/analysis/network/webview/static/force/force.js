/* force directed graph with direction arrows and multiple edges

References

http://jsfiddle.net/zhanghuancs/a2QpA/
https://bl.ocks.org/mattkohl/146d301c0fc20d89d85880df537de7b0
http://bl.ocks.org/fancellu/2c782394602a93921faff74e594d1bb1
*/


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
function arcPath(leftHand, d) {
    // var isOddLink = d.linkindex % 2 === 0;
    var x1 = (leftHand) ? d.source.x : d.target.x,
        y1 = (leftHand) ? d.source.y : d.target.y,
        x2 = (leftHand) ? d.target.x : d.source.x,
        y2 = (leftHand) ? d.target.y : d.source.y,
        dx = x2 - x1,
        dy = y2 - y1,
        dr = Math.sqrt(dx * dx + dy * dy);

    var sweep = (leftHand) ? 0 : 1;

    xRotation = 0,
        largeArc = 0;

    var dx = d.target.x - d.source.x,
        dy = d.target.y - d.source.y,
        dr = Math.sqrt(dx * dx + dy * dy);

    // get the total link numbers between source and target node
    var siblingCount = mLinkNum[d.source.id + "," + d.target.id] || mLinkNum[d.target.id + "," + d.source.id];
    if (siblingCount > 1) {
        // if there are multiple links between these two nodes, we need generate different dr for each path
        dr = dr / (1 + (1 / (siblingCount)) * (d.linkindex - 1 - sweep));
    }

    return "M" + x1 + "," + y1 + "A" + dr + ", " + dr + " " + xRotation + ", " + largeArc + ", " + sweep + " " + x2 + "," + y2;
}

var colors = d3.scaleOrdinal(d3.schemeCategory10);

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height"),
    node,
    link,
    pathInvis;

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


var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) { return d.id; }).distance(500).strength(0.5))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));


d3.json("force/force.json", function (error, graph) {
    if (error) throw error;
    var linksData = graph.links
    sortLinks(linksData)
    setLinkIndexAndNum(linksData)
    update(linksData, graph.nodes);
});

function update(links, nodes) {
    link = svg.selectAll(".link")
        .data(links)
        .enter()
        // .append("line")
        .append("svg:path")
        .attr("class", "link")
        .attr('marker-end', 'url(#arrowhead)')

    link.append("title")
        .text(function (d) { return d.name; });

    pathInvis = svg.selectAll(".pathInvis")
        .data(links)
        .enter()
        // .append("line")
        .append("svg:path")
        .attr("id", function (d) {
            return 'invis_' + d.source + "-" + d.linkindex + "-" + d.target;
        })
        .attr("class", "pathInvis")

    var pathLabel = svg.selectAll(".pathLabel")
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
    node = svg.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            //.on("end", dragended)
        );

    node.append("circle")
        .attr("r", 5)
        .style("fill", function (d, i) { return colors(i); })

    node.append("title")
        .text(function (d) { return d.id; });

    node.append("text")
        .attr("dy", -3)
        .text(function (d) { return d.name + ":" + d.text; });

    simulation
        .nodes(nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(links);
}


function ticked() {
    link.attr("d", function (d) {
        return arcPath(true, d);
    });

    pathInvis.attr("d", function (d) {
        return arcPath(d.source.x < d.target.x, d);
    });

    node.attr("transform", function (d) { return "translate(" + d.x + ", " + d.y + ")"; });
}

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.02).restart()
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

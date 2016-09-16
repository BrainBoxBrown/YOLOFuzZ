
// get the data
d3.json("force.json", function(json) {

var nodes = {};

// Compute the distinct nodes from the links.
// links.forEach(function(link) {
//     link.source = nodes[link.source] || 
//         (nodes[link.source] = {name: link.source});
//     link.target = nodes[link.target] || 
//         (nodes[link.target] = {name: link.target});
//     link.value = +link.value;
// });

var width = 10000,
    height = 10000;

var force = d3.layout.force()
    .nodes(json.nodes)
    .links(json.links)
    .size([width, height])
    .linkDistance(10)
    .linkStrength(function(x) { return Math.sqrt(x.weight) || 1; })
    .charge(-100)
    .on("tick", tick)
    .start();



var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

// build the arrow.
svg.append("svg:defs").selectAll("marker")
    .data(["end"])      // Different link/path types can be defined here
  .enter().append("svg:marker")    // This section adds in the arrows
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15)
    .attr("refY", -1.5)
    .attr("markerWidth", 6)
    .attr("markerHeight", 10)
    .attr("orient", "auto")
  .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");

// add the links and the arrows
var path = svg.append("svg:g").selectAll("path")
    .data(json.links)
  .enter().append("svg:path")
//    .attr("class", function(d) { return "link " + d.type; })
    .attr("class", "link")
    .attr("marker-end", "url(#end)");

// define the nodes
var node = svg.selectAll(".node")
    .data(json.nodes)
  .enter().append("g")
    .attr("class", "node")
    .call(force.drag);

// add the text 
node.append("text")
    .attr("x", 12)
    .attr("dy", ".35em")
    .text(function(d) { return d.name; });

// add the nodes
node.append("circle")
    // .attr("r", 5)
    .attr("r", function(d) {return 3*Math.sqrt(d.predecessors) || 1; });

// add the curvy lines
function tick() {
    path.attr("d", function(d) {
        var dx = d.target.x - d.source.x,
            dy = d.target.y - d.source.y,
            dr = Math.sqrt(dx * dx + dy * dy)**1.2;
        return "M" + 
            d.source.x + "," + 
            d.source.y + "A" + 
            dr + "," + dr + " 0 0,0 " + 
            d.target.x + "," + 
            d.target.y;
    });

    node
        .attr("transform", function(d) { 
        return "translate(" + d.x + "," + d.y + ")"; });
}

});
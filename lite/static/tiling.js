/**
 * Simple Web Map tile algorithm
 */
let tiling = (function() {
    let ns = {}

    /**
     * Estimate Z/X/Y tile indices related to viewport
     */
    ns.tiles = function(x_range, y_range, limits) {
        // World coordinates in Google Maps API terminology
        let interpX = interp1d(limits.x[0], limits.x[1], 0, 256)
        let interpY = interp1d(limits.y[0], limits.y[1], 0, 256)
        let world = {
            x: {
                start: interpX(x_range.start),
                end: interpX(x_range.end)
            },
            y: {
                start: interpY(y_range.start),
                end: interpY(y_range.end)
            }
        }
        let level = zoomLevel(world)
        // Calculate {Z} {X} {Y} values
        let indices = {
            x: {
                start: tileIndex(pixelIndex(world.x.start, level)),
                end: tileIndex(pixelIndex(world.x.end, level)),
            },
            y: {
                start: tileIndex(pixelIndex(world.y.start, level)),
                end: tileIndex(pixelIndex(world.y.end, level)),
            },
        }
        let tiles = []
        for (let i=indices.x.start; i<=indices.x.end; i++) {
            for (let j=indices.y.start; j<=indices.y.end; j++) {
                tiles.push({
                    z: level,
                    x: i,
                    y: j,
                })
            }
        }
        return tiles
    }

    // Simple 1d interpolator
    let interp1d = ns.interp1d = function(xLow, xHigh, yLow, yHigh) {
        let wrapped = function(x) {
            return ((yHigh - yLow) * (x - xLow)) / (xHigh - xLow)
        }
        return wrapped
    }

    // Pixel index related to zoom level
    let pixelIndex = ns.pixelIndex = function(x, level) {
        return Math.floor(x * (2**level))
    }

    // Tile index from pixel index assuming 256x256 tile
    let tileIndex = ns.tileIndex = function(pixel) {
        return Math.floor(pixel / 256)
    }

    // Optimal zoom level given world coordinates
    let zoomLevel = ns.zoomLevel = function(world) {
        // TODO: support negative
        let dx = world.x.end - world.x.start
        let dy = world.y.end - world.y.start
        let dw = Math.min(dx, dy)
        return Math.floor(Math.log2(256 / dw))
    }

    return ns
})()

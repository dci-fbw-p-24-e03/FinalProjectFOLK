/** 
 * Col
 * Stores occupancy information (0 = free, 1 = used) for each row in a single column.
 */
class Col {
    constructor(rows) {
        // Create an array of `rows` length, each entry initialized to 0 (unused).
        this.rows = Array.from({ length: rows }, () => 0);
        this.free = rows; // Tracks how many cells in this column are still free.
    }
}

/** 
 * Circuit
 * Represents a single “path” or route of connected cells from a start cell to an end cell.
 */
class Circuit {
    constructor(start, size) {
        this.start = start;     // [x, y] cell coordinates for the start
        this.cellSize = size;   // Size in pixels of each cell in the grid
        this.path = [];         // Sequence of directional steps ([dx, dy]) from start to end
        this.end = null;        // [x, y] cell coordinates for the end
        this.things = [];       // Moving objects (Things) that travel along this path
        this.length = 0;        // Total length in pixels of the path
        this.coords = [];       // Absolute cell coordinates that the path passes through
    }
}

/** 
 * Circuits
 * Builds multiple Circuit objects, ensures they don't overlap, and draws them to a canvas. 
 */
class Circuits {
    constructor(width, height, size, minLength, maxLength) {
        this.size = size;
        this.width = width;
        this.height = height;
        this.cols = Math.floor(width / size);
        this.rows = Math.floor(height / size);

        // Create an array of Col objects to track occupancy for each column.
        this.scene = Array.from({ length: this.cols }, () => new Col(this.rows));

        // Holds all generated circuits
        this.collection = [];

        this.minLength = minLength;
        this.maxLength = maxLength;

        // Generate circuits and immediately draw them
        this.populate();
        this.draw();
    }

    /** 
     * draw() 
     * Creates an offscreen canvas and renders all circuits as lines + arcs.
     */
    draw() {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const size = this.size;

        canvas.width = this.width;
        canvas.height = this.height;

        // First pass: draw the path lines
        ctx.strokeStyle = 'rgba(59, 177, 188, 1)';
        ctx.lineWidth = Math.round(size / 10);

        this.collection.forEach(circuit => {
            let point = [circuit.start[0], circuit.start[1]];
            const path = circuit.path;

            // Begin drawing from the center of the start cell
            ctx.beginPath();
            ctx.moveTo(
                point[0] * size + size / 2 + path[0][0] * size / 4,
                point[1] * size + size / 2 + path[0][1] * size / 4
            );

            // Follow each directional step in circuit.path
            path.forEach((dir, index) => {
                point[0] += dir[0];
                point[1] += dir[1];

                // For the last segment, move the end slightly “inward” for a smoother line
                if (index === path.length - 1) {
                    ctx.lineTo(
                        point[0] * size + size / 2 - dir[0] * size / 4,
                        point[1] * size + size / 2 - dir[1] * size / 4
                    );
                } else {
                    ctx.lineTo(
                        point[0] * size + size / 2,
                        point[1] * size + size / 2
                    );
                }
            });
            ctx.stroke();
        });

        // Second pass: draw arcs on start/end points for a stylized “connection” look
        ctx.lineWidth = Math.floor(this.size / 5);
        ctx.strokeStyle = 'rgba(59, 177, 188, 0.6)';
        this.collection.forEach(circuit => {
            ctx.beginPath();
            ctx.arc(
                circuit.start[0] * size + size / 2,
                circuit.start[1] * size + size / 2,
                size / 4, 0, 2 * Math.PI, false
            );
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(
                circuit.end[0] * size + size / 2,
                circuit.end[1] * size + size / 2,
                size / 4, 0, 2 * Math.PI, false
            );
            ctx.stroke();
        });

        this.canvas = canvas;
    }

    /** 
     * populate() 
     * Randomly tries to place circuits in free cells. Each circuit has a random length
     * within [minLength, maxLength]. 
     */
    populate() {
        const size = this.size;
        let start = null;
        // 'n' is a safeguard to prevent infinite loops if there's no space left
        let n = 1000;

        while ((start = this.getStart()) && n--) {
            const length = this.minLength + Math.floor(Math.random() * (this.maxLength - this.minLength));
            let dir = this.getDir(start);

            // Mark the start cell as used
            this.setUsed(start[0], start[1]);

            // If a valid direction is returned, build a new circuit
            if (dir[0] !== 0 || dir[1] !== 0) {
                const circuit = new Circuit(start, size);
                let moving = true;
                const path = [start[0], start[1]];
                let coords = [start[0], start[1]];
                let stepsLeft = length - 1;

                while (moving && stepsLeft) {
                    circuit.path.push(dir);
                    circuit.coords.push([path[0], path[1]]);

                    path[0] += dir[0];
                    path[1] += dir[1];

                    // Mark new cell as used
                    this.setUsed(path[0], path[1]);

                    // Decide next direction
                    dir = this.getDir(path, dir);
                    if (dir[0] === 0 && dir[1] === 0) {
                        moving = false;
                    }
                    stepsLeft--;
                }

                // Once we can’t go further or we run out of steps, finalize the circuit
                if (circuit.path.length >= this.minLength) {
                    circuit.end = path;
                    circuit.coords.push([path[0], path[1]]);

                    // Add traveling “things” that move along this circuit
                    // "things" is a global instance of class Things (see below).
                    let speed = Math.random() * 0.5 + 0.5;
                    circuit.things.push(things.create(circuit, speed * 1));

                    if (circuit.path.length > this.maxLength / 3) {
                        speed = Math.random() * 0.5 + 0.5;
                        circuit.things.push(things.create(circuit, -speed, circuit.path.length * size));
                    }
                    if (circuit.path.length > this.maxLength / 1.5) {
                        speed = Math.random() * 0.5 + 0.5 * (Math.random() >= 0.5 ? -1 : 1);
                        circuit.things.push(things.create(circuit, speed, Math.random() * circuit.path.length * size));
                    }

                    // Save overall pixel length of the path
                    circuit.length = circuit.path.length * size;

                    // Store the new circuit
                    this.collection.push(circuit);
                }
            }
        }
    }

    /** 
     * getStart() 
     * Chooses a random column that has at least one free cell, then returns 
     * [colIndex, rowIndex] of one free cell. 
     */
    getStart() {
        const scene = this.scene;
        const freeCols = [];

        // Gather columns that still have free cells
        scene.forEach((col, index) => {
            if (col.free) {
                freeCols.push(index);
            }
        });

        if (freeCols.length) {
            const chosenCol = this.pickOne(freeCols);
            const freeCells = [];

            // Gather row indices that are free in chosen column
            scene[chosenCol].rows.forEach((cellValue, rowIndex) => {
                if (cellValue === 0) {
                    freeCells.push(rowIndex);
                }
            });

            const chosenRow = this.pickOne(freeCells);
            return [chosenCol, chosenRow];
        }
        return false;
    }

    /** 
     * pickOne() 
     * Helper to pick a random element from an array.
     */
    pickOne(array) {
        return array[Math.floor(Math.random() * array.length)];
    }

    /**
     * setUsed(x, y)
     * Marks the cell at [x, y] as occupied in this.scene.
     */
    setUsed(x, y) {
        this.scene[x].rows[y] = 1;
        this.scene[x].free--;
    }

    /**
     * isAvailable(x, y)
     * Checks if the cell [x, y] is in-range and unoccupied.
     */
    isAvailable(x, y) {
        const scene = this.scene;
        if (scene[x] && scene[x].rows[y] === 0) {
            return true;
        }
        return false;
    }

    /** 
     * getDir(fromPoint, oldDir = null)
     * Picks a direction [dx, dy] from the current cell that’s still free.
     * If oldDir is provided, there's a 50% chance to keep going in the same direction.
     */
    getDir(fromPoint, oldDir = null) {
        // Possibly keep the current direction
        if (oldDir && Math.random() <= 0.5) {
            if (this.isAvailable(fromPoint[0] + oldDir[0], fromPoint[1] + oldDir[1])) {
                return oldDir;
            }
        }

        const possibleX = [];
        const possibleY = [];
        const result = [0, 0];

        // Horizontal moves
        if (this.isAvailable(fromPoint[0] - 1, fromPoint[1])) {
            possibleX.push(-1);
        }
        if (this.isAvailable(fromPoint[0] + 1, fromPoint[1])) {
            possibleX.push(1);
        }

        // Vertical moves
        if (this.isAvailable(fromPoint[0], fromPoint[1] - 1)) {
            possibleY.push(-1);
        }
        if (this.isAvailable(fromPoint[0], fromPoint[1] + 1)) {
            possibleY.push(1);
        }

        // Pick horizontal 50% of the time if available, else vertical
        if (possibleX.length && Math.random() < 0.5) {
            result[0] = this.pickOne(possibleX);
        } else if (possibleY.length) {
            result[1] = this.pickOne(possibleY);
        }
        return result;
    }
}

/** 
 * Dots
 * Creates a small dotted background with a specified spacing. 
 * Each dot is drawn once (in draw()) and also stored in this.dots for later reference.
 */
class Dots {
    constructor(width, height, spacing) {
        this.spacing = spacing;
        this.dots = [];

        // Create offscreen canvas for drawing
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = width;
        canvas.height = height;
        this.canvas = canvas;
        this.ctx = ctx;

        this.draw();
    }

    /** 
     * draw() 
     * Fills the offscreen canvas with faint dots at each [x * spacing, y * spacing].
     */
    draw() {
        const { ctx, spacing } = this;
        ctx.fillStyle = 'rgba(24, 129, 141, 0.1)';

        // Build dot info and draw each dot on the offscreen canvas
        const cols = Math.floor(this.canvas.width / spacing);
        const rows = Math.floor(this.canvas.height / spacing);

        this.dots = Array.from({ length: cols }, (_, x) => {
            return Array.from({ length: rows }, (_, y) => {
                const dot = {
                    opacity: 0.1,
                    x: x * spacing,
                    y: y * spacing
                };
                ctx.fillRect(dot.x, dot.y, 1, 1);
                return dot;
            });
        });
    }

    /** 
     * ghost() 
     * Creates a second canvas with solid dots (used later for masking in "Things"). 
     */
    ghost() {
        const ghostDots = document.createElement('canvas');
        ghostDots.width = this.canvas.width;
        ghostDots.height = this.canvas.height;

        const dotsCtx = ghostDots.getContext('2d');
        dotsCtx.fillStyle = 'rgb(24, 129, 141)';

        // Fill each dot as a 1x1 block
        this.dots.forEach(col => {
            col.forEach(dot => {
                dotsCtx.fillRect(dot.x, dot.y, 1, 1);
            });
        });
        return ghostDots;
    }
}

/** 
 * Thing
 * A small moving object that travels along a circuit path (Circuit object). 
 * Can have a velocity in either direction along the path, plus optional start delays and lifetimes.
 */
class Thing {
    constructor(
        circuit,
        velocity,
        done = 0,
        startDelay = Math.floor(Math.random() * 600) + 1,
        lifetime = 300
    ) {
        this.circuit = circuit;
        this.velocity = velocity;
        this.done = done;
        this.x = 0;
        this.y = 0;
        this.startDelay = startDelay;  // Frames to wait before activation is possible
        this.lifetime = lifetime;      // How many frames to remain alive once active
        this.active = false;           // Manager will flip this to true when there's room
    }

    update() {
        // 1) If we are NOT active:
        if (!this.active) {
            // Decrement startDelay (cannot go below 0)
            if (this.startDelay > 0) {
                this.startDelay--;
            }
            // Then we're done for this frame—no movement/lifetime checks
            return;
        }

        // 2) If we ARE active:
        // Decrement lifetime if not infinite
        if (this.lifetime !== Infinity) {
            this.lifetime--;
            // If lifetime expired, become inactive
            if (this.lifetime <= 0) {
                this.active = false;
                return;
            }
        }

        // Perform normal movement along the circuit path
        const { cellSize: size, length, path, start, end, coords } = this.circuit;

        // “done” tracks how many pixels along the path we’ve traveled
        this.done += this.velocity;

        // Bounce if we exceed boundaries
        if (this.done <= 0) {
            this.done = 0;
            this.velocity = -this.velocity;
        } else if (this.done >= length) {
            this.done = length;
            this.velocity = -this.velocity;
        }

        // Figure out where we are (x,y) along the path
        let x = 0, y = 0;
        if (this.done <= size / 2) {
            // Very close to the start
            x = (start[0] * size + size / 2) + this.done * path[0][0];
            y = (start[1] * size + size / 2) + this.done * path[0][1];
        } else if (this.done > (length - size / 2)) {
            // Very close to the end
            const lastDir = path[path.length - 1];
            x = (end[0] * size + size / 2) - (length - this.done) * lastDir[0];
            y = (end[1] * size + size / 2) - (length - this.done) * lastDir[1];
        } else {
            // Middle of the path; figure out which segment we're on
            const index = Math.floor(this.done / size);
            const doneInSegment = this.done - index * size;
            const dir = [path[index][0], path[index][1]];
            const point = coords[index];

            x = point[0] * size + size / 2 + doneInSegment * dir[0];
            y = point[1] * size + size / 2 + doneInSegment * dir[1];
        }

        this.x = Math.floor(x);
        this.y = Math.floor(y);
    }

    // Optional “reset” logic if you want to re-use the same Thing multiple times
    reset() {
        this.startDelay = Math.floor(Math.random() * 100);
        this.lifetime = 300;
        this.done = 0;
        this.active = false;
    }

    // Measures how close we are to a sibling on the same circuit
    distFromSister() {
        let dist = Infinity;
        this.circuit.things.forEach(other => {
            if (other !== this) {
                const tmp = Math.abs(other.done - this.done);
                if (tmp < dist) {
                    dist = tmp;
                }
            }
        });
        return dist;
    }
}


/**
 * Things
 * A manager that holds and updates multiple “Thing” objects traveling along circuits. 
 * Also handles drawing them with glow effects clipped by the dotted background.
 */
class Things {
    constructor(width, height) {
        this.width = width;
        this.height = height;

        // Offscreen canvas for drawing glow overlays
        this.canvas = document.createElement('canvas');
        this.canvas.width = width;
        this.canvas.height = height;
        this.ctx = this.canvas.getContext('2d');

        // Collection of all Thing objects
        this.collection = [];
    }

    // Provide a helper to get the count of active items
    getActiveCount() {
        return this.collection.filter(t => t.active).length;
    }

    /**
     * create(circuit, velocity, done = 0)
     * Factory method that instantiates a new Thing and adds it to the collection.
     */
    create(circuit, velocity, done = 0) {
        const thing = new Thing(circuit, velocity, done);
        this.collection.push(thing);
        return thing;
    }

    /**
     * update()
     * 1) Let each Thing do its update (movement if active, or waiting if inactive)
     * 2) Enforce that at most 10 can be active by only activating some if under the limit
     */
    update() {
        // STEP 1: Update each Thing
        this.collection.forEach(thing => thing.update());

        // STEP 2: Remove truly “dead” ones from the array
        //         i.e. not active and not waiting for startDelay
        this.collection = this.collection.filter(t => t.active || t.startDelay > 0);

        // STEP 3: Count how many are active
        const activeCount = this.getActiveCount();

        // STEP 4: If fewer than 10 are active, spawn brand-new ones
        if (activeCount < 10) {
            const toCreate = 10 - activeCount;
            for (let i = 0; i < toCreate; i++) {
                const c = circuits.collection[
                  Math.floor(Math.random() * circuits.collection.length)
                ];
                const speed = (Math.random() * 0.5 + 0.5) * (Math.random() < 0.5 ? -1 : 1);
                // create a new Thing
                const newT = this.create(c, speed);
              
                // Force it active immediately
                newT.active = true;
                // Possibly set newT.startDelay = 0; 
                // so it won't get removed
              }
        }
    }

    /**
     * draw()
     * Renders active Things with glow effects, clipping them to only show “over” the dotted pattern.
     */
    draw() {
        const ctx = this.ctx;
        const radius = this.lightRadius;
        const space = radius / 3;  // Threshold for “close” siblings

        ctx.clearRect(0, 0, this.width, this.height);

        // Filter only the active Things
        const activeThings = this.collection.filter(thing => thing.active);

        // Draw at most the first 10
        activeThings.slice(0, 10).forEach(thing => {
            let radial = this.ghostRadial;
            let diffX = radius, diffY = radius;

            // If this Thing is close to a sibling, switch to a bigger glow
            if (thing.distFromSister() <= space) {
                radial = this.ghostSuperRadial;
                diffX = radial.width / 2;
                diffY = radial.height / 2;
            }

            ctx.drawImage(radial, thing.x - diffX, thing.y - diffY, radial.width, radial.height);
        });

        // Clip the glow so it only appears where the dotted pattern is
        ctx.save();
        ctx.globalCompositeOperation = 'destination-in';
        ctx.drawImage(this.dotsGhost, 0, 0);
        ctx.restore();

        // Draw small bright circles at the center of each Thing
        ctx.save();
        ctx.globalCompositeOperation = 'source-over';
        ctx.fillStyle = '#afe3e9';

        activeThings.slice(0, 10).forEach(thing => {
            ctx.beginPath();
            ctx.arc(thing.x, thing.y, radius / 6, 0, 2 * Math.PI, false);
            ctx.fill();
        });
        ctx.restore();
    }

    /**
     * setDotsGhost(canvas)
     * Stores a "ghost" version of the dotted background (solid dots) 
     * for use as a clipping mask.
     */
    setDotsGhost(canvas) {
        this.dotsGhost = canvas;
    }

    /**
     * setLight(lightRadius)
     * Creates radial glow textures used when drawing the moving “Things.”
     */
    setLight(lightRadius) {
        this.lightRadius = lightRadius;

        // Smaller glow
        this.ghostRadial = document.createElement('canvas');
        this.ghostRadial.width = lightRadius * 2;
        this.ghostRadial.height = lightRadius * 2;

        const radialCtx = this.ghostRadial.getContext('2d');
        let gradient = radialCtx.createRadialGradient(
            lightRadius, lightRadius, lightRadius,
            lightRadius, lightRadius, 0
        );
        gradient.addColorStop(0, "rgba(24, 129, 141, 0)");
        gradient.addColorStop(1, "rgba(24, 129, 141, 0.6)");

        radialCtx.fillStyle = gradient;
        radialCtx.fillRect(0, 0, lightRadius * 2, lightRadius * 2);

        // Larger “starburst” glow for close-together Things
        this.ghostSuperRadial = document.createElement('canvas');
        const radWidth = this.ghostSuperRadial.width = lightRadius * 15;
        const radHeight = this.ghostSuperRadial.height = lightRadius * 20;
        const superRadialCtx = this.ghostSuperRadial.getContext('2d');

        gradient = superRadialCtx.createRadialGradient(
            radWidth / 2, radHeight / 2, radWidth / 2,
            radWidth / 2, radHeight / 2, 0
        );
        gradient.addColorStop(0, "rgba(37, 203, 223, 0)");
        gradient.addColorStop(1, "rgba(37, 203, 223, 0.4)");

        superRadialCtx.fillStyle = gradient;
        superRadialCtx.beginPath();
        superRadialCtx.moveTo(radWidth / 2 + lightRadius / 6, radHeight / 2 - lightRadius / 3);
        // The star-like shape's polygon is drawn here
        superRadialCtx.lineTo(radWidth, 0);
        superRadialCtx.lineTo(radWidth / 2 + lightRadius / 3, radHeight / 2 - lightRadius / 6);
        superRadialCtx.lineTo((3 * radWidth) / 4, radHeight / 2);
        superRadialCtx.lineTo(radWidth / 2 + lightRadius / 3, radHeight / 2 + lightRadius / 6);
        superRadialCtx.lineTo(radWidth, radHeight);
        superRadialCtx.lineTo(radWidth / 2 + lightRadius / 6, radHeight / 2 + lightRadius / 3);
        superRadialCtx.lineTo(radWidth / 2, (3 * radHeight) / 4);
        superRadialCtx.lineTo(radWidth / 2 - lightRadius / 6, radHeight / 2 + lightRadius / 3);
        superRadialCtx.lineTo(0, radHeight);
        superRadialCtx.lineTo(radWidth / 2 - lightRadius / 3, radHeight / 2 + lightRadius / 6);
        superRadialCtx.lineTo(radWidth / 4, radHeight / 2);
        superRadialCtx.lineTo(radWidth / 2 - lightRadius / 3, radHeight / 2 - lightRadius / 6);
        superRadialCtx.lineTo(0, 0);
        superRadialCtx.lineTo(radWidth / 2 - lightRadius / 6, radHeight / 2 - lightRadius / 3);
        superRadialCtx.lineTo(radWidth / 2, radHeight / 4);
        superRadialCtx.lineTo(radWidth / 2 + lightRadius / 6, radHeight / 2 - lightRadius / 3);
        superRadialCtx.fill();
    }
}

/** 
 * Background
 * Combines dots and circuit lines into one static image that can be drawn behind animations.
 */
class Background {
    constructor(width, height) {
        this.width = width;
        this.height = height;
    }

    /** 
     * getBackground() 
     * Returns a new canvas with dots + circuits drawn on a black background.
     */
    getBackground() {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = this.width;
        canvas.height = this.height;

        // Simple black fill
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, this.width, this.height);

        // Overlay the dotted layer and then the circuits
        ctx.drawImage(dots.canvas, 0, 0);
        ctx.drawImage(circuits.canvas, 0, 0);

        return canvas;
    }
}

/* ---------------
   Main Logic
   ---------------
*/

// Connect to a <canvas> element in the DOM
const bgCanvas = document.getElementById('circuit-bg');
const width = bgCanvas.width = window.innerWidth;
const height = bgCanvas.height = window.innerHeight;
const bgCtx = bgCanvas.getContext('2d');

// Create a dotted background
const dots = new Dots(width, height, 2);

// Create a manager for moving “things”
const things = new Things(width, height);
things.setDotsGhost(dots.ghost());
things.setLight(dots.spacing * 4);

// Create circuits (lines) on a grid
const maxLength = 16;
const minLength = 3;
const cellSize = 10;
const circuits = new Circuits(width, height, cellSize, minLength, maxLength);

// Generate one static “background” combining dots + circuits
const background = new Background(width, height);
const staticBG = background.getBackground();
bgCtx.drawImage(staticBG, 0, 0);

// Create a separate canvas for the animation layers on top
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');

canvas.width = width;
canvas.height = height;
document.body.appendChild(canvas);

/** 
 * loop() 
 * Animation loop: clears the overlay, updates & draws the “things,” then requests the next frame.
 */
function loop() {
    ctx.clearRect(0, 0, width, height);
    things.update();
    things.draw();
    ctx.drawImage(things.canvas, 0, 0);

    requestAnimationFrame(loop);
}

// Start the animation
loop();

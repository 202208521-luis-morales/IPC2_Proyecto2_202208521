let db = [{
  filename: String,
  drones: ["drones_names"],
  systems: [{
    name: String,
    dronesSystems: [{
      drone: String,
      system: [{
        height: Number,
        text: String,
      }]
    }]
  }],
  messages: [{
    name: String,
    dronesSystem: String,
    instructions: [{
      drone: String,
      moveNum: Number,
      status: String // "not-executed" | "executed" | "executing"
    }]
  }],
  processedData: [{
    messageName: String,
    finalMessage: String,
    rows: [{
      time: Number,
      instdrones: [{
        drone: String,
        inst: String,
      }]
    }]
  }]
}];

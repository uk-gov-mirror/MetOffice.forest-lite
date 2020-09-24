import * as Redux from "redux"
import React from "react"
import ReactDOM from "react-dom"
import { Provider } from "react-redux"
import App from "./App.js"
import { rootReducer } from "./reducers.js"
import { toolMiddleware } from "./middlewares.js"
import { colorPaletteMiddleware } from "./colorpalette-middleware.js"
import { timeMiddleware } from "./time-middleware.js"
import {
    SET_DATASETS,
    NEXT_TIME_INDEX,
    PREVIOUS_TIME_INDEX
} from "./action-types.js"
import {
    set_dataset,
    set_datasets,
    set_playing,
    set_limits,
    set_time_index,
    next_time_index,
    previous_time_index,
    fetch_image,
    fetch_image_success
} from "./actions.js"


// ReduxJS

// Middlewares
let logActionMiddleware = store => next => action => {
    console.log(action)
    next(action)
}

let animationMiddleware = store => next => action => {
    if (action.type === NEXT_TIME_INDEX) {
        let state = store.getState()
        if (typeof state.time_index === "undefined") {
            return
        }
        if (typeof state.times === "undefined") {
            return
        }
        let index = mod(state.time_index + 1, state.times.length)
        let action = set_time_index(index)
        next(action)
    } else if (action.type === PREVIOUS_TIME_INDEX) {
        let state = store.getState()
        if (typeof state.time_index === "undefined") {
            return
        }
        if (typeof state.times === "undefined") {
            return
        }
        let index = mod(state.time_index - 1, state.times.length)
        let action = set_time_index(index)
        next(action)
    } else {
        next(action)
    }
}

let datasetsMiddleware = store => next => action => {
    next(action)
    if (action.type == SET_DATASETS) {
        const { dataset } = store.getState()
        if (typeof dataset !== "undefined") {
            let dataset_id = action.payload[0].id
            next(set_dataset(dataset_id))
        }
    }
    return
}


// Helpers
let mod = function(a, n) {
    // Always return positive number, e.g. mod(-2, 5) -> 3
    // Builtin % operator allows negatives, e.g. -2 % 5 -> -2
    return ((a % n) + n) % n
}


window.main = function(baseURL) {
    let store = Redux.createStore(rootReducer,
                                  Redux.applyMiddleware(
                                      logActionMiddleware,
                                      toolMiddleware,
                                      animationMiddleware,
                                      colorPaletteMiddleware,
                                      timeMiddleware,
                                      datasetsMiddleware,
                                  ))
    store.subscribe(() => { console.log(store.getState()) })

    // Use React to manage components
    ReactDOM.render(
        <Provider store={store}>
            <App baseURL={ baseURL } />
        </Provider>,
        document.getElementById("root"))

    // Fetch datasets from server
    fetch(`${baseURL}/datasets`)
        .then(response => response.json())
        .then(data => data.datasets)
        .then(datasets => store.dispatch(set_datasets(datasets)))

    //   // RESTful image
    //   let image_source = new Bokeh.ColumnDataSource({
    //       data: {
    //           x: [],
    //           y: [],
    //           dw: [],
    //           dh: [],
    //           image: [],
    //           url: []
    //       }
    //   })
    //   let filter = new Bokeh.IndexFilter({
    //       indices: []
    //   })
    //   let view = new Bokeh.CDSView({
    //       source: image_source,
    //       filters: []
    //   })
    //   // image_source.connect(image_source.properties.data.change, () => {
    //   //     const arrayMax = array => array.reduce((a, b) => Math.max(a, b))
    //   //     const arrayMin = array => array.reduce((a, b) => Math.min(a, b))
    //   //     let image = image_source.data.image[0]
    //   //     let low = arrayMin(image.map(arrayMin))
    //   //     let high = arrayMax(image.map(arrayMax))
    //   //     let action = set_limits({low, high})
    //   //     store.dispatch(action)
    //   // })
    //   store.dispatch(set_limits({low: 200, high: 300}))
    //   store.subscribe(() => {
    //       let state = store.getState()
    //       if (state.is_fetching) {
    //           return
    //       }
    //       if (typeof state.dataset === "undefined") {
    //           return
    //       }
    //       if (typeof state.time_index === "undefined") {
    //           return
    //       }
    //       if (typeof state.times === "undefined") {
    //           return
    //       }

    //       // Fetch image if not already loaded
    //       let time = state.times[state.time_index]
    //       let url = `${baseURL}/datasets/${state.dataset}/times/${time}`
    //       if (state.image_url === url) {
    //           return
    //       }

    //       let index = image_source.data["url"].indexOf(url)
    //       if (index >= 0) {
    //           view.indices = [index]
    //           return
    //       }

    //       store.dispatch(fetch_image(url))
    //       fetch(url).then((response) => {
    //           return response.json()
    //       }).then((data) => {
    //           // fix missing wiring in image_base.ts
    //           // image_source._shapes = {
    //           //     image: [
    //           //         []
    //           //     ]
    //           // }

    //           let newData = Object.keys(data).reduce((acc, key) => {
    //               acc[key] = image_source.data[key].concat(data[key])
    //               return acc
    //           }, {})
    //           newData["url"] = image_source.data["url"].concat([url])

    //           image_source.data = newData
    //           image_source.change.emit()
    //       }).then(() => {
    //           store.dispatch(fetch_image_success())
    //       })
    //   })

    //   window.image_source = image_source
    //   let glyph = figure.image({
    //       x: { field: "x" },
    //       y: { field: "y" },
    //       dw: { field: "dw" },
    //       dh: { field: "dh" },
    //       image: { field: "image" },
    //       source: image_source,
    //       view: view,
    //       color_mapper: color_mapper
    //   })
    //

    // Set static limits
    store.dispatch(set_limits({low: 200, high: 300}))

    let frame = () => {
        let state = store.getState()
        if (state.is_fetching) {
            return
        }
        if (state.playing) {
            let action = next_time_index()
            store.dispatch(action)
        }
    }

    // Animation mechanism
    let interval = 100
    // setInterval(frame, interval)
    // setTimeout(frame, interval)
    frame()
    setInterval(frame, interval)

}

import React from "react"
import AnimationControls from "./AnimationControls.js"
import MapFigure from "./MapFigure.js"
import Title from "./Title.js"
import Toolbar from "./Toolbar.js"
import Colorbar from "./Colorbar.js"
import LayerMenu from "./LayerMenu.js"
import LocalStorage from "./LocalStorage.js"


class Panel extends React.Component {
    render() {
        const { baseURL } = this.props
        const style = {
            padding: "4px",
            zIndex: 5
        }
        return (
            <div style={ style } >
                <Toolbar />
                <LayerMenu baseURL={ baseURL } />
            </div>)
    }
}

class App extends React.Component {
    render() {
        const { baseURL } = this.props
        return (
            <div>
                <LocalStorage />
                <Title />
                <Panel baseURL={ baseURL } />
                <div className="colorbar-container">
                    <Colorbar />
                    <AnimationControls />
                </div>
                <MapFigure baseURL={ baseURL } />
            </div>
        )
    }
}


export default App

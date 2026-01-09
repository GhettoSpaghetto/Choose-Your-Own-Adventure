import React from "react";

function LoadingStatus({theme}){
    return <div className="loading-container">
        <h2>Generating Your theme</h2>


        <div className="loading-animation">
            <div className="spinner"></div>
        </div>

        <p className="loading-info">Please wait while generate your story</p>
    </div>
}



export default LoadingStatus;
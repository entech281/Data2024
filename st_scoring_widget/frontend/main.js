// The `Streamlit` object exists because our html file includes
// `streamlit-component-lib.js`.
// If you get an error about "Streamlit" not being defined, that
// means you're missing that file.


var currentValues = [
    0,0,
    0,0,
    0,0,
    0,0
];

function resetValues(){
    currentValues = [
        0,0,
        0,0,
        0,0,
        0,0
    ]
}

function update_component() {
     Streamlit.setComponentValue(currentValues);
}

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event) {
  // Only run the render code the first time the component is loaded.
  if (!window.rendered) {

    // later, convert to more dynamic
    //const {labels} = event.detail.args;

    const amp_score = document.getElementById("amp_score");
    const amp_miss = document.getElementById("amp_miss");
    const amp_value = document.getElementById("amp_value");

    const subwoofer_score = document.getElementById("subwoofer_score");
    const subwoofer_miss = document.getElementById("subwoofer_miss");
    const subwoofer_value = document.getElementById("subwoofer_value");

    const podium_score = document.getElementById("podium_score");
    const podium_miss = document.getElementById("podium_miss");
    const podium_value = document.getElementById("podium_value");

    const far_score = document.getElementById("far_score");
    const far_miss = document.getElementById("far_miss");
    const far_value = document.getElementById("far_value");

    function update(){
        update_component();
        amp_value.innerText = currentValues[0] + " | " + currentValues[1];
        subwoofer_value.innerText = currentValues[2] + " | " + currentValues[3];
        podium_value.innerText = currentValues[4] + " | " + currentValues[5];
        far_value.innerText = currentValues[6] + " | " + currentValues[7];
    }
    document.getElementById("clear").onclick = function(e){
        resetValues();
        update();
    }
    amp_score.onclick = function(e){
        currentValues[1]++;
        update();

    }
    amp_miss.onclick = function(e){
        currentValues[0]++;
        update();

    }

    subwoofer_score.onclick = function(e){
        currentValues[3]++;
        update();

    }
    subwoofer_miss.onclick = function(e){
        currentValues[2]++;
        update();
    }

    podium_score.onclick = function(e){
        currentValues[5]++;
        update();
    }
    podium_miss.onclick = function(e){
        currentValues[4]++;
        update();
    }

    far_score.onclick = function(e){
        currentValues[7]++;
        update();
    }
    far_miss.onclick = function(e){
        currentValues[6]++;
        update();
    }
    update();

    window.rendered = true
  }
}

// Render the component whenever python send a "render event"
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
// Tell Streamlit that the component is ready to receive events
Streamlit.setComponentReady()
// Render with the correct height, if this is a fixed-height component
Streamlit.setFrameHeight(230)


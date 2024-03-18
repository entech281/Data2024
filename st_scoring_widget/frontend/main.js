// The `Streamlit` object exists because our html file includes
// `streamlit-component-lib.js`.
// If you get an error about "Streamlit" not being defined, that
// means you're missing that file.

var currentValues = [
    0,0,
    0,0,
    0,0,
    0,0
]


function update() {
  Streamlit.setComponentValue(currentValues)
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

    amp_score.onclick = function(e){
        currentValues[0]++;
        update();
        amp_value.innerText = currentValues[1] + " | " + currentValues[0];
    }
    amp_miss.onclick = function(e){
        currentValues[1]++;
        update();
        amp_value.innerText = currentValues[1] + " | " + currentValues[0];
    }

    subwoofer_score.onclick = function(e){
        currentValues[2]++;
        update();
        subwoofer_value.innerText = currentValues[3] + " | " + currentValues[2];
    }
    subwoofer_miss.onclick = function(e){
        currentValues[3]++;
        update();
        subwoofer_value.innerText = currentValues[3] + " | " + currentValues[2];
    }

    podium_score.onclick = function(e){
        currentValues[4]++;
        update();
        podium_value.innerText = currentValues[5] + " | " + currentValues[4];
    }
    podium_miss.onclick = function(e){
        currentValues[5]++;
        update();
        podium_value.innerText = currentValues[5] + " | " + currentValues[4];
    }

    far_score.onclick = function(e){
        currentValues[6]++;
        update();
        far_value.innerText = currentValues[7] + " | " + currentValues[6];
    }
    far_miss.onclick = function(e){
        currentValues[7]++;
        update();
        far_value.innerText = currentValues[7] + " | " + currentValues[6];
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
Streamlit.setFrameHeight(200)


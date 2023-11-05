import * as THREE from 'three';
import {TrackballControls} from 'three/addons/controls/TrackballControls.js';
import {DragControls} from 'three/addons/controls/DragControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {GLTFExporter} from 'three/addons/exporters/GLTFExporter.js';
import {GUI} from 'three/addons/libs/lil-gui.module.min.js';

/**
 * Config constants
 */

const ADVERSARY_URL = "/data/organisms";
const TACTIC_URL = "/data/families";
const GRAPH_URL = "/graph/";

/**
 * GUI Variables
 */

let camera;
let scene;
let renderer;
let controls;
let gui;
let drag_controls;
let mouse_x = 0;
let mouse_y = 0;

let graph;

let species_data = {};

const node_geometry = new THREE.SphereGeometry(0.75, 16, 16);

const node_material = new THREE.MeshStandardMaterial({
  color: 0x049ef4,
  emissive: 0x000000,
  side: THREE.FrontSide,
  flatShading: false,
  roughness: 0.5,
  metalness: 0
});

const edge_material = new THREE.MeshStandardMaterial({
  color: 0xebecef,
  emissive: 0x072534,
  side: THREE.FrontSide,
  flatShading: false,
  roughness: 0.5,
  metalness: 0.5
});

const get_material = (color) => {
  return new THREE.MeshStandardMaterial({
    color,
    emissive: 0x000000,
    side: THREE.FrontSide,
    flatShading: false,
    roughness: 0.5,
    metalness: 0
  })
};


const debug = (msg) => {
  if (guiData.debug) {
    log(msg)
  }
};

const log = (msg) => {
  const el = document.getElementById("console");
  if (!el) {
    console.log(msg);
  } else {
    el.innerHTML += "<br/>" + msg;
  }
};

const init = () => new Promise((resolve) => {
  log("Starting UI...");

  const aspect = window.innerWidth / window.innerHeight;
  log("Creating camera...");
  camera = new THREE.PerspectiveCamera(60, aspect, 1, 1000);
  camera.position.z = 100;

  log("Creating scene...");
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);
  scene.fog = new THREE.Fog(0x000000, 5, 1000);

  // lights
  log("Creating lights...");
  const lights = [];
  lights[0] = new THREE.DirectionalLight(0xffffff, 3);
  lights[1] = new THREE.DirectionalLight(0xffffff, 3);
  lights[2] = new THREE.DirectionalLight(0xffffff, 3);

  lights[0].position.set(0, 200, 0);
  lights[1].position.set(100, 200, 100);
  lights[2].position.set(-100, -200, -100);

  scene.add(lights[0]);
  scene.add(lights[1]);
  scene.add(lights[2]);

  const axesHelper = new THREE.AxesHelper(5);
  scene.add(axesHelper);

  gui = new GUI();

  gui.add(guiData, 'debug');
  gui.add(guiData, 'export');

  log("Creating renderer...");
  const canvas = document.getElementById("puppy");
  renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true
  });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);

  canvas.onmousemove = (evt) => {
    mouse_x = evt.offsetX;
    mouse_y = evt.offsetY;
    document.getElementById("coord").innerHTML = "X:" + evt.offsetX + ",Y:" + evt.clientY;
  };

  log("Appending renderer to page...");
  document.body.appendChild(renderer.domElement);

  window.addEventListener('resize', onWindowResize);

  resolve();
});

const createControls = () => new Promise((resolve) => {
  log("Creating controls...");
  controls = new TrackballControls(camera, renderer.domElement);

  controls.rotateSpeed = 3;
  controls.zoomSpeed = 1.2;
  controls.panSpeed = 0.5;

  controls.keys = ['KeyA', 'KeyS', 'KeyD'];
  log("Controls created...");
  resolve();
});

const onWindowResize = () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize(window.innerWidth, window.innerHeight);

  controls.handleResize();
};

const animate = () => {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
};

const exportGlTF = () => new Promise(resolve => {
  if (!graph) {
    log("No graph defined");
    return;
  }
  log("Exporting GLTF...");
  const exporter = new GLTFExporter();
  exporter.parse(
      graph,
      (gltf) => {
        log("glTF ready...");
        download(gltf);
        resolve();
      },
      (error) => console.error(error)
  );
});

const download = (gltf) => {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(gltf));
  const downloadAnchorNode = document.createElement('a');
  downloadAnchorNode.setAttribute("href", dataStr);
  downloadAnchorNode.setAttribute("download", "graph.gltf");
  document.body.appendChild(downloadAnchorNode); // required for firefox
  downloadAnchorNode.click();
  downloadAnchorNode.remove();
};

const fetchAdversaries = () => {
  log("Fetching ATT&CK adversary groups...");
  return fetch(ADVERSARY_URL).then((response) => response.json());
};

const adversaryToUi = (adversaries) => {
  log(`Retrieved ${Object.keys(adversaries).length} adversary groups`);
  const options = {
    // 'None': 1,
    // 'Other': 2
  };
  adversaries.sort((a, b) => {
    const A = a.name.toUpperCase();
    const B = b.name.toUpperCase();
    if (A < B) {
      return -1;
    }
    if (A > B) {
      return 1;
    }
    return 0;
  });
  adversaries.forEach(g => {
    options[g.name] = g.id;
  });
  gui.add(guiData, 'group', options).onChange(fetchAdversary);
  log(`Adversary groups added`);
};

const fetchAdversary = (adversaryId) => {
  log("Fetching ATT&CK graph for adversary");
  log(adversaryId);

  fetch(GRAPH_URL + adversaryId)
      .then((response) => response.json())
      .then(renderAdversary);
};

const renderAdversary = (graphData) => {
  debug(graphData);
  log("Removing existing graph");
  scene.remove(graph);

  log("Removing drag controls");
  if (drag_controls) {
    drag_controls.deactivate();
    drag_controls.dispose();
    drag_controls = null;
  }

  const objects = [];

  species_data = {};

  log("Generating new graph");
  graph = new THREE.Group();

  graph.name = "graph_group";

  // let classification = graphData[0];
  graphData.forEach(classification => {
    let color = 0x049ef4;
    let level = 5;
    if (classification.hasOwnProperty('family')) {
      color = classification.family.color;
      level = classification.family.orbit;
    }
    const level_orbit = new THREE.SphereGeometry(level, 8, 8);
    const level_material = new THREE.MeshBasicMaterial({color: 0x333333, wireframe: true, fog: true});
    const orbit = new THREE.Mesh(level_orbit, level_material);
    graph.add(orbit);

    const material = get_material(color);
    if (classification.hasOwnProperty('species')) {
      classification.species.forEach(species => {
        const renderNode = new THREE.Mesh(node_geometry, material);
        renderNode.position.set(species.pos[0], species.pos[1], species.pos[2]);
        renderNode.name = species.id;

        species_data[species.id] = species;

        graph.add(renderNode);
        objects.push(renderNode);
      });
    }
  });

  drag_controls = new DragControls([...objects], camera, renderer.domElement);
  drag_controls.addEventListener('hoveron', (evt) => {
    const el = document.getElementById("label");
    el.style.left = mouse_x + "px";
    el.style.top = mouse_y + "px";

    const sp = species_data[evt.object.name];

    let text = evt.object.name;

    if (sp) {
      text = sp.id
          + "<br/>"
          + sp.external_id
          + "<br/>"
          + sp.name
          + "<br/>"
          + sp.type;
    }

    el.innerHTML = text;
    el.classList.remove('hidden');
  });
  drag_controls.addEventListener('hoveroff', (evt) => {
    const el = document.getElementById("label");
    el.classList.add('hidden');
  });

  // Object.keys(graphData["nodes"]).forEach(node => {
  //   debug("Rendering node " + node + "@" + graphData["nodes"][node]['pos']);
  //   const renderNode = new THREE.Mesh(node_geometry, node_material);
  //   renderNode.position.set(
  //       graphData["nodes"][node]['pos'][0],
  //       graphData["nodes"][node]['pos'][1],
  //       graphData["nodes"][node]['pos'][2],
  //   );
  //   graph.add(renderNode);
  // });
  //
  // graphData["edges"].forEach(edge => {
  //   const curve = new THREE.LineCurve3(
  //       new THREE.Vector3(edge[0][0], edge[0][1], edge[0][2]),
  //       new THREE.Vector3(edge[1][0], edge[1][1], edge[1][2]),
  //   );
  //   const edge_geometry = new THREE.TubeGeometry(curve, 20, 0.1, 16, false);
  //
  //   const renderEdge = new THREE.Mesh(edge_geometry, edge_material);
  //   graph.add(renderEdge);
  // });

  debug("Adding graph to scene");
  scene.add(graph);

  log("Graph generated");

};

const guiData = {
  group: 'None',
  debug: false,
  'export': exportGlTF
};

init()
    .then(() => createControls())
    .then(() => animate())
    .then(fetchAdversaries)
    .then(adversaryToUi)
;
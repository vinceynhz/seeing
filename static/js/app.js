import * as THREE from 'three';
import {TrackballControls} from 'three/addons/controls/TrackballControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {GLTFExporter} from 'three/addons/exporters/GLTFExporter.js';
import {GUI} from 'three/addons/libs/lil-gui.module.min.js';

let camera;
let scene;
let renderer;
let controls;
let gui;

let graph;

const node_geometry = new THREE.SphereGeometry(1, 32, 16);
const node_material = new THREE.MeshStandardMaterial({
  color: 0x049ef4,
  emissive: 0x072534,
  side: THREE.FrontSide,
  flatShading: false,
  roughness: 0.5,
  metalness: 0.5
});

const edge_material = new THREE.MeshStandardMaterial({
  color: 0xebecef,
  emissive: 0x072534,
  side: THREE.FrontSide,
  flatShading: false,
  roughness: 0.5,
  metalness: 0.5
});


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

  gui.add(guiData, 'export');

  log("Creating renderer...");
  renderer = new THREE.WebGLRenderer({antialias: true});
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);

  log("Appending renderer to page...");
  document.body.appendChild(renderer.domElement);

  window.addEventListener('resize', onWindowResize);

  resolve();
});

const generate_stuff = () => new Promise((resolve) => {
  log("Generating stuff...");
  // const geometry = new THREE.BoxGeometry(10, 10, 10, 1, 1, 1);

  graph = new THREE.Group();
  graph.name = "graph_group";

  const cube1 = new THREE.Mesh(node_geometry, node_material);
  cube1.position.set(10, 10, 0);

  const cube2 = new THREE.Mesh(node_geometry, node_material);
  cube2.position.set(-10, -10, 0);

  const cube3 = new THREE.Mesh(node_geometry, node_material);
  cube3.position.set(0, 0, 20);



  graph.add(cube1);
  graph.add(cube2);
  graph.add(cube3);
  graph.add(edge1);

  scene.add(graph);

  log("Stuff generated...");
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
  if(!graph) {
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

const fetchGroups = () => {
  log("Fetching ATT&CK adversary groups...");
  return fetch('/data/groups').then((response) => response.json());
};

const groupsToUI = (groups) => {
  log(`Retrieved ${Object.keys(groups).length} groups`);
  const options = {
    // 'None': 1,
    // 'Other': 2
  };
  groups.sort((a, b) => {
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
  groups.forEach(g => {
    options[g.name] = g.id;
  });
  gui.add(guiData, 'group', options).onChange(fetchGroup);
  log(`Groups added`);
};

const fetchGroup = (groupId) => {
  log("Fetching ATT&CK graph for adversary");
  log(groupId);

  fetch('/graph/' + groupId)
      .then((response) => response.json())
      .then(renderGroup);
};

const renderGroup = (graphData) => {
  log("Removing existing graph");
  scene.remove(graph);

  graph = new THREE.Group();
  graph.name = "graph_group";

  Object.keys(graphData["nodes"]).forEach(node => {
    log("Rendering node " + node + "@" + graphData["nodes"][node]['pos']);
    const renderNode = new THREE.Mesh(node_geometry, node_material);
    renderNode.position.set(
        graphData["nodes"][node]['pos'][0],
        graphData["nodes"][node]['pos'][1],
        graphData["nodes"][node]['pos'][2],
    );
    graph.add(renderNode);
  });

  graphData["edges"].forEach(edge => {
    const curve = new THREE.LineCurve3(
        new THREE.Vector3(edge[0][0], edge[0][1], edge[0][2]),
        new THREE.Vector3(edge[1][0], edge[1][1], edge[1][2]),
    );
    const edge_geometry = new THREE.TubeGeometry(curve, 20, 0.1, 16, false);

    const renderEdge = new THREE.Mesh(edge_geometry, edge_material);
    graph.add(renderEdge);
  });

  log("Adding graph to scene");
  scene.add(graph);

  log("Graph generated...");

};

const guiData = {
  group: 'None',
  'export': exportGlTF
};

init()
// .then(() => loadModel())
//     .then(() => generate_stuff())
    .then(() => createControls())
    // .then(() => exportGlTF())
    .then(() => animate())
    .then(fetchGroups)
    .then(groupsToUI)
;
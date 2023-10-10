# About the process

This application 

### Step 1: Define Domain and Data Structure

- Define the domain for which you want to create a 3D graph visualization. Understand the structure and nature of the data within the domain.
- Identify the information that will be represented in the 3D graph and define the relevant schema or metadata for the data.
- Choose the parameters that will be used to create the 3D graph, including the attributes that will become nodes and edges.

### Step 2: Data to General Graph Model

- Convert instances of the metadata or domain-specific data into a general graph model. This model should include nodes and edges that represent the data relationships.
- Use the "type" property to categorize nodes and edges and correlate them with domain metadata.

### Step 3: Processing Pipeline Setup

- Review the processing pipeline and tools to be used.
- Utilize Python to convert the general graph model (in JSON or another format) into a NetworkX graph, which will serve as the basis for generating 3D coordinates.
- Define the skeleton of the glTF (GL Transmission Format) model, including nodes and edges.
- Use domain-specific metadata to generate aesthetic components of the visualization, such as textures or colors.

### Step 4: Generate glTF Model

- Utilize the processed data and the NetworkX graph to generate the glTF model, ensuring that it adheres to the skeleton structure defined in Step 3.
- Incorporate the 3D coordinates generated for nodes into the glTF model.
- Include any domain-specific textures, materials, or visual attributes in the glTF model.

### Step 5: Web Application Integration

- Create a web application, preferably using a library like Three.js, to render and interact with the 3D graph visualization.
- Load the generated glTF model into the web application and set up the rendering environment.
- Implement interactivity and user controls to allow users to explore and interact with the 3D graph.
  
### Step 6: Review and Refine

- Review the 3D graph visualization to ensure it meets the project goals and requirements.
- Make refinements as necessary to improve the clarity, aesthetics, and user experience of the visualization.

### Step 7: Documentation and Sharing

- Document the entire process, including data conversion, graph generation, glTF model creation, and web application development.
- Share the 3D graph visualization with your intended audience, providing clear instructions on how to access and interact with it.

### Step 8: Maintenance and Updates

- If the project involves dynamic data or changes over time, establish mechanisms for updating and maintaining the 3D graph visualization.
- Ensure that the web application remains compatible with the evolving data.

### Step 9: User Engagement and Feedback

- Encourage user engagement and gather feedback to continuously improve the 3D graph visualization.
- Consider incorporating user suggestions for enhancements or additional features.

## References

* [Three JS examples](https://threejs.org/examples/?q=contro#misc_controls_map)
flask upload
* [MITRE ATT&CK Repo](https://github.com/mitre-attack/attack-stix-data)
* [MITRE ATT&CK Matrix Design and Philosophy Whitepaper](https://attack.mitre.org/docs/ATTACK_Design_and_Philosophy_March_2020.pdf)
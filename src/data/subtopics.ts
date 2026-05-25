/**
 * Nested curriculum data — sub-topics and leaf exercises for every module.
 *
 * Keyed by module idx ('00'..'15'). Rendered by the § 2 Curriculum section on
 * the landing page, alongside the flat MODULES catalog in `./modules.ts`.
 *
 * A leaf with `lessonSlug` is rendered as a link to /lessons/<slug>;
 * without it, the leaf is rendered dim ("not yet migrated"). As new MDX
 * lessons are added under src/content/lessons/, set their slug here.
 */

export interface LeafEntry {
  id: string;             // "1.1.1", "12.3.2"
  title: string;
  /** Lesson slug under src/content/lessons/. Undefined → rendered dim. */
  lessonSlug?: string;
}

export interface SubtopicEntry {
  id: string;             // "1.1", "12.3"
  title: string;
  leaves: LeafEntry[];
}

export const SUBTOPICS: Record<string, SubtopicEntry[]> = {
  '00': [
    { id: '0.1', title: 'What Is Generative Art', leaves: [
      { id: '0.1', title: 'What Is Generative Art' },
    ]},
    { id: '0.2', title: 'Defining AI / ML / Algorithms', leaves: [
      { id: '0.2', title: 'Defining AI ML Algorithms' },
    ]},
    { id: '0.4', title: 'Setup & Environment', leaves: [
      { id: '0.4', title: 'Setup Environment' },
    ]},
  ],

  '01': [
    { id: '1.1', title: 'Grayscale & Color Basics', leaves: [
      { id: '1.1.1', title: 'Color Basics', lessonSlug: '1.1.1' },
      { id: '1.1.2', title: 'Color Theory Spaces (HSV, LAB)' },
    ]},
    { id: '1.2', title: 'Pixel Manipulation Patterns', leaves: [
      { id: '1.2.1', title: 'Random Patterns' },
      { id: '1.2.2', title: 'Cellular Automata' },
      { id: '1.2.3', title: 'Reaction Diffusion' },
    ]},
    { id: '1.3', title: 'Structured Compositions', leaves: [
      { id: '1.3.1', title: 'Flags' },
      { id: '1.3.2', title: 'Repeat' },
      { id: '1.3.3', title: 'Truchet Tiles' },
      { id: '1.3.4', title: 'Wang Tiles' },
    ]},
  ],

  '02': [
    { id: '2.1', title: 'Basic Shapes & Primitives', leaves: [
      { id: '2.1.1', title: 'Lines' },
      { id: '2.1.2', title: 'Triangles' },
      { id: '2.1.3', title: 'Circles' },
      { id: '2.1.4', title: 'Stars' },
      { id: '2.1.5', title: 'Polygons & Polyhedra' },
    ]},
    { id: '2.2', title: 'Coordinate Systems & Fields', leaves: [
      { id: '2.2.1', title: 'Gradient' },
      { id: '2.2.2', title: 'Spiral' },
      { id: '2.2.3', title: 'Vector Fields' },
      { id: '2.2.4', title: 'Distance Fields' },
    ]},
    { id: '2.3', title: 'Mathematical Art', leaves: [
      { id: '2.3.1', title: 'Lissajous Curves' },
      { id: '2.3.2', title: 'Rose Curves' },
      { id: '2.3.3', title: 'Harmonograph Simulation' },
      { id: '2.3.4', title: 'Strange Attractors' },
    ]},
  ],

  '03': [
    { id: '3.1', title: 'Geometric Transformations', leaves: [
      { id: '3.1.1', title: 'Rotation' },
      { id: '3.1.2', title: 'Affine Transformations' },
      { id: '3.1.3', title: 'Nonlinear Distortions' },
      { id: '3.1.4', title: 'Kaleidoscope Effects' },
    ]},
    { id: '3.2', title: 'Masking & Compositing', leaves: [
      { id: '3.2.1', title: 'Mask' },
      { id: '3.2.2', title: 'Meme Generator' },
      { id: '3.2.3', title: 'Shadow' },
      { id: '3.2.4', title: 'Blend Modes' },
    ]},
    { id: '3.3', title: 'Artistic Filters', leaves: [
      { id: '3.3.1', title: 'Warhol' },
      { id: '3.3.2', title: 'Puzzle (Array Concatenation)' },
      { id: '3.3.3', title: 'Hexpanda' },
      { id: '3.3.4', title: 'Voronoi Diagrams' },
      { id: '3.3.5', title: 'Delaunay Triangulation' },
    ]},
    { id: '3.4', title: 'Signal Processing', leaves: [
      { id: '3.4.1', title: 'Convolution' },
      { id: '3.4.2', title: 'Edge Detection (Sobel)' },
      { id: '3.4.3', title: 'Contour Lines' },
      { id: '3.4.4', title: 'Fourier Art' },
    ]},
  ],

  '04': [
    { id: '4.1', title: 'Classical Fractals', leaves: [
      { id: '4.1.1', title: 'Fractal Square', lessonSlug: '4.1.1' },
      { id: '4.1.2', title: 'Dragon Curve' },
      { id: '4.1.3', title: 'Mandelbrot' },
      { id: '4.1.4', title: 'Julia Sets' },
      { id: '4.1.5', title: 'Sierpinski' },
    ]},
    { id: '4.2', title: 'Natural Fractals', leaves: [
      { id: '4.2.1', title: 'Fractal Trees' },
      { id: '4.2.2', title: 'Lightning Bolts' },
      { id: '4.2.3', title: 'Fractal Landscapes' },
      { id: '4.2.4', title: 'Diffusion-Limited Aggregation' },
    ]},
    { id: '4.3', title: 'L-Systems', leaves: [
      { id: '4.3.1', title: 'Plant Generation' },
      { id: '4.3.2', title: 'Koch Snowflake' },
      { id: '4.3.3', title: 'Penrose Tiling' },
    ]},
  ],

  '05': [
    { id: '5.1', title: 'Particle Systems', leaves: [
      { id: '5.1.1', title: 'Sand' },
      { id: '5.1.2', title: 'Vortex' },
      { id: '5.1.3', title: 'Fireworks Simulation' },
      { id: '5.1.4', title: 'Fluid Simulation' },
    ]},
    { id: '5.2', title: 'Flocking & Swarms', leaves: [
      { id: '5.2.1', title: 'Boids' },
      { id: '5.2.2', title: 'Fish Schooling' },
      { id: '5.2.3', title: 'Ant Colony Optimization' },
    ]},
    { id: '5.3', title: 'Physics Simulations', leaves: [
      { id: '5.3.1', title: 'Bouncing Ball Animation' },
      { id: '5.3.2', title: 'N-Body Planet Simulation' },
      { id: '5.3.3', title: 'Double Pendulum Chaos' },
      { id: '5.3.4', title: 'Cloth / Rope Simulation' },
      { id: '5.3.5', title: 'Magnetic Field Visualization' },
    ]},
    { id: '5.4', title: 'Growth & Morphogenesis', leaves: [
      { id: '5.4.1', title: 'Eden Growth Model' },
      { id: '5.4.2', title: 'Differential Growth' },
      { id: '5.4.3', title: 'Space Colonization' },
      { id: '5.4.4', title: 'Turing Patterns' },
    ]},
  ],

  '06': [
    { id: '6.1', title: 'Noise Functions', leaves: [
      { id: '6.1.1', title: 'Perlin Noise' },
      { id: '6.1.2', title: 'Simplex Noise' },
      { id: '6.1.3', title: 'Worley Noise' },
      { id: '6.1.4', title: 'Colored Noise' },
    ]},
    { id: '6.2', title: 'Terrain Generation', leaves: [
      { id: '6.2.1', title: 'Height Maps' },
      { id: '6.2.2', title: 'Erosion Simulation' },
      { id: '6.2.3', title: 'Cave Generation' },
      { id: '6.2.4', title: 'Island Generation' },
    ]},
    { id: '6.3', title: 'Texture Synthesis', leaves: [
      { id: '6.3.1', title: 'Marble & Wood' },
      { id: '6.3.2', title: 'Cloud Generation' },
      { id: '6.3.3', title: 'Abstract Patterns' },
      { id: '6.3.4', title: 'Procedural Materials' },
    ]},
    { id: '6.4', title: 'Wave & Interference Patterns', leaves: [
      { id: '6.4.1', title: 'Moiré Patterns' },
      { id: '6.4.2', title: 'Wave Interference' },
      { id: '6.4.3', title: 'Cymatics' },
    ]},
  ],

  '07': [
    { id: '7.1', title: 'Clustering & Segmentation', leaves: [
      { id: '7.1.1', title: 'K-Means Clustering' },
      { id: '7.1.2', title: 'Mean-Shift Segmentation' },
      { id: '7.1.3', title: 'DBSCAN Pattern Detection' },
    ]},
    { id: '7.2', title: 'Classification & Recognition', leaves: [
      { id: '7.2.1', title: 'Decision Tree Classifier' },
      { id: '7.2.2', title: 'Random Forests' },
      { id: '7.2.3', title: 'SVM Style Detection' },
    ]},
    { id: '7.3', title: 'Dimensionality Reduction', leaves: [
      { id: '7.3.1', title: 'PCA Color Palette' },
      { id: '7.3.2', title: 't-SNE Visualization' },
      { id: '7.3.3', title: 'UMAP Visualizations' },
    ]},
    { id: '7.4', title: 'Statistical Methods', leaves: [
      { id: '7.4.1', title: 'Monte Carlo Sampling' },
      { id: '7.4.2', title: 'Markov Chains' },
      { id: '7.4.3', title: 'Hidden Markov Models' },
    ]},
  ],

  '08': [
    { id: '8.1', title: 'Animation Fundamentals', leaves: [
      { id: '8.1.1', title: 'Image Transformations' },
      { id: '8.1.2', title: 'Easing Functions' },
      { id: '8.1.3', title: 'Interpolation Techniques' },
      { id: '8.1.4', title: 'Sprite Sheets' },
    ]},
    { id: '8.2', title: 'Organic Motion', leaves: [
      { id: '8.2.1', title: 'Flower Assembly' },
      { id: '8.2.2', title: 'Infinite Blossom' },
      { id: '8.2.3', title: 'Walk Cycles' },
      { id: '8.2.4', title: 'Breathing / Pulsing' },
    ]},
    { id: '8.3', title: 'Cinematic Effects', leaves: [
      { id: '8.3.1', title: 'Star Wars Titles' },
      { id: '8.3.2', title: 'Thank You' },
      { id: '8.3.3', title: 'Particle Text Reveals' },
      { id: '8.3.4', title: 'Morphing Transitions' },
    ]},
    { id: '8.4', title: 'Generative Animation', leaves: [
      { id: '8.4.1', title: 'Music Visualization' },
      { id: '8.4.2', title: 'Data-Driven Animation' },
      { id: '8.4.3', title: 'Animated Fractals' },
    ]},
  ],

  '09': [
    { id: '9.1', title: 'Neural Network Fundamentals', leaves: [
      { id: '9.1.1', title: 'Perceptron from Scratch' },
      { id: '9.1.2', title: 'Backpropagation Visualization' },
      { id: '9.1.3', title: 'Activation Functions Art' },
    ]},
    { id: '9.2', title: 'Network Architectures', leaves: [
      { id: '9.2.1', title: 'Feedforward Networks' },
      { id: '9.2.2', title: 'Convolutional Networks' },
      { id: '9.2.3', title: 'Recurrent Networks' },
    ]},
    { id: '9.3', title: 'Training Dynamics', leaves: [
      { id: '9.3.1', title: 'Loss Landscape' },
      { id: '9.3.2', title: 'Gradient Descent Animation' },
      { id: '9.3.3', title: 'Overfitting / Underfitting' },
    ]},
    { id: '9.4', title: 'Feature Visualization', leaves: [
      { id: '9.4.1', title: 'DeepDream' },
      { id: '9.4.2', title: 'Feature Map Art' },
      { id: '9.4.3', title: 'Network Attention' },
    ]},
  ],

  '10': [
    { id: '10.1', title: 'TD Environment & Workflow', leaves: [
      { id: '10.1.1', title: 'Node Networks' },
      { id: '10.1.2', title: 'Python Integration Basics' },
      { id: '10.1.3', title: 'Performance Monitoring' },
    ]},
    { id: '10.2', title: 'Recreating Static Exercises', leaves: [
      { id: '10.2.1', title: 'Core Exercises Realtime' },
      { id: '10.2.2', title: 'Boids in TouchDesigner' },
      { id: '10.2.3', title: 'Planet Simulation TD' },
      { id: '10.2.4', title: 'Fractals Realtime' },
    ]},
    { id: '10.3', title: 'NumPy ↔ TD Pipeline', leaves: [
      { id: '10.3.1', title: 'Script Operators' },
      { id: '10.3.2', title: 'Array Processing' },
      { id: '10.3.3', title: 'Custom Components' },
    ]},
    { id: '10.4', title: 'Interactive Controls', leaves: [
      { id: '10.4.1', title: 'UI Building' },
      { id: '10.4.2', title: 'Parameter Mapping' },
      { id: '10.4.3', title: 'Preset Systems' },
    ]},
  ],

  '11': [
    { id: '11.1', title: 'Input Devices', leaves: [
      { id: '11.1.1', title: 'Webcam Processing' },
      { id: '11.1.2', title: 'Audio Reactivity' },
      { id: '11.1.3', title: 'MIDI / OSC Control' },
      { id: '11.1.4', title: 'Kinect / Leap Motion' },
    ]},
    { id: '11.2', title: 'Computer Vision in TD', leaves: [
      { id: '11.2.1', title: 'Motion Detection' },
      { id: '11.2.2', title: 'Blob Tracking' },
      { id: '11.2.3', title: 'Face Detection' },
      { id: '11.2.4', title: 'Optical Flow' },
    ]},
    { id: '11.3', title: 'Physical Computing', leaves: [
      { id: '11.3.1', title: 'Arduino Integration' },
      { id: '11.3.2', title: 'DMX Lighting Control' },
      { id: '11.3.3', title: 'Projection Mapping' },
    ]},
    { id: '11.4', title: 'Network Communication', leaves: [
      { id: '11.4.1', title: 'Multi-Machine Setups' },
      { id: '11.4.2', title: 'WebSocket / WebRTC' },
      { id: '11.4.3', title: 'Remote Control Interfaces' },
    ]},
  ],

  '12': [
    { id: '12.1', title: 'Generative Adversarial Networks', leaves: [
      { id: '12.1.1', title: 'GAN Architecture' },
      { id: '12.1.2', title: 'DCGAN Art', lessonSlug: '12.1.2' },
      { id: '12.1.3', title: 'StyleGAN Exploration' },
      { id: '12.1.4', title: 'Pix2Pix Applications' },
    ]},
    { id: '12.2', title: 'Variational Autoencoders', leaves: [
      { id: '12.2.1', title: 'Latent Space Exploration' },
      { id: '12.2.2', title: 'Interpolation Animations' },
      { id: '12.2.3', title: 'Conditional VAEs' },
    ]},
    { id: '12.3', title: 'Diffusion Models', leaves: [
      { id: '12.3.1', title: 'DDPM Basics' },
      { id: '12.3.2', title: 'ControlNet Guided Generation' },
    ]},
    { id: '12.4', title: 'Bridging Paradigms', leaves: [
      { id: '12.4.1', title: 'Neural Style Transfer' },
      { id: '12.4.2', title: 'VQ-VAE & VQ-GAN' },
    ]},
    { id: '12.5', title: 'Personalization & Efficiency', leaves: [
      { id: '12.5.1', title: 'DreamBooth Personalization' },
    ]},
    { id: '12.6', title: 'Transformer Generation', leaves: [
      { id: '12.6.1', title: 'Taming Transformers' },
      { id: '12.6.2', title: 'Diffusion Transformer (DiT)' },
    ]},
    { id: '12.7', title: 'Modern Frontiers', leaves: [
      { id: '12.7.1', title: 'Flow Matching' },
    ]},
  ],

  '13': [
    { id: '13.1', title: 'ML Models in TD', leaves: [
      { id: '13.1.1', title: 'MediaPipe Integration' },
      { id: '13.1.2', title: 'RunwayML Bridge' },
      { id: '13.1.3', title: 'ONNX Runtime' },
    ]},
    { id: '13.2', title: 'Real-time AI Effects', leaves: [
      { id: '13.2.1', title: 'Style Transfer Live' },
      { id: '13.2.2', title: 'Realtime Segmentation' },
      { id: '13.2.3', title: 'Pose-Driven Effects' },
    ]},
    { id: '13.3', title: 'Generative Models Live', leaves: [
      { id: '13.3.1', title: 'GAN Inference Optimization' },
      { id: '13.3.2', title: 'Latent Space Navigation UI' },
      { id: '13.3.3', title: 'Model Switching Systems' },
    ]},
    { id: '13.4', title: 'Hybrid Pipelines', leaves: [
      { id: '13.4.1', title: 'Preprocessing in TD' },
      { id: '13.4.2', title: 'Python ML Processing' },
      { id: '13.4.3', title: 'Post-Processing Chains' },
    ]},
  ],

  '14': [
    { id: '14.1', title: 'Data Sources', leaves: [
      { id: '14.1.1', title: 'APIs & Data Scraping' },
      { id: '14.1.2', title: 'Sensor Networks' },
      { id: '14.1.3', title: 'Social Media Streams' },
      { id: '14.1.4', title: 'Environmental Data' },
    ]},
    { id: '14.2', title: 'Visualization Techniques', leaves: [
      { id: '14.2.1', title: 'Network Graphs' },
      { id: '14.2.2', title: 'Flow Visualization' },
      { id: '14.2.3', title: 'Multidimensional Scaling' },
      { id: '14.2.4', title: 'Time Series Art' },
    ]},
    { id: '14.3', title: 'Sonification', leaves: [
      { id: '14.3.1', title: 'Data to Sound Mapping' },
      { id: '14.3.2', title: 'Granular Synthesis' },
      { id: '14.3.3', title: 'Rhythmic Patterns' },
    ]},
    { id: '14.4', title: 'Physical Data Sculptures', leaves: [
      { id: '14.4.1', title: '3D Printing Preparation' },
      { id: '14.4.2', title: 'Laser Cutting Patterns' },
      { id: '14.4.3', title: 'CNC Toolpaths' },
    ]},
  ],

  '15': [
    { id: '15', title: 'Synthesis Project', leaves: [
      { id: '15', title: 'Eternal Flow — capstone' },
    ]},
  ],
};

/**
 * Aggregate counts for a module. `shipped` is the count of leaves whose
 * MDX lesson exists; useful for debugging but the public UI does not
 * surface it.
 */
export function countLeaves(idx: string): { subs: number; leaves: number; shipped: number } {
  const subs = SUBTOPICS[idx] ?? [];
  let leaves = 0;
  let shipped = 0;
  for (const s of subs) {
    for (const l of s.leaves) {
      leaves++;
      if (l.lessonSlug) shipped++;
    }
  }
  return { subs: subs.length, leaves, shipped };
}

/** Flat list of all leaves in a module, in display order. */
export function leavesFor(moduleIdx: string): LeafEntry[] {
  const subs = SUBTOPICS[moduleIdx] ?? [];
  return subs.flatMap(s => s.leaves);
}

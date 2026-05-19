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
      { id: '0.1', title: 'What Is Generative Art', lessonSlug: '0.1' },
    ]},
    { id: '0.2', title: 'Defining AI / ML / Algorithms', leaves: [
      { id: '0.2', title: 'Defining AI ML Algorithms', lessonSlug: '0.2' },
    ]},
    { id: '0.4', title: 'Setup & Environment', leaves: [
      { id: '0.4', title: 'Setup Environment', lessonSlug: '0.4' },
    ]},
  ],

  '01': [
    { id: '1.1', title: 'Grayscale & Color Basics', leaves: [
      { id: '1.1.1', title: 'Color Basics', lessonSlug: '1.1.1' },
      { id: '1.1.2', title: 'Color Theory Spaces (HSV, LAB)', lessonSlug: '1.1.2' },
    ]},
    { id: '1.2', title: 'Pixel Manipulation Patterns', leaves: [
      { id: '1.2.1', title: 'Random Patterns', lessonSlug: '1.2.1' },
      { id: '1.2.2', title: 'Cellular Automata', lessonSlug: '1.2.2' },
      { id: '1.2.3', title: 'Reaction Diffusion', lessonSlug: '1.2.3' },
    ]},
    { id: '1.3', title: 'Structured Compositions', leaves: [
      { id: '1.3.1', title: 'Flags', lessonSlug: '1.3.1' },
      { id: '1.3.2', title: 'Repeat', lessonSlug: '1.3.2' },
      { id: '1.3.3', title: 'Truchet Tiles', lessonSlug: '1.3.3' },
      { id: '1.3.4', title: 'Wang Tiles', lessonSlug: '1.3.4' },
    ]},
  ],

  '02': [
    { id: '2.1', title: 'Basic Shapes & Primitives', leaves: [
      { id: '2.1.1', title: 'Lines', lessonSlug: '2.1.1' },
      { id: '2.1.2', title: 'Triangles', lessonSlug: '2.1.2' },
      { id: '2.1.3', title: 'Circles', lessonSlug: '2.1.3' },
      { id: '2.1.4', title: 'Stars', lessonSlug: '2.1.4' },
      { id: '2.1.5', title: 'Polygons & Polyhedra', lessonSlug: '2.1.5' },
    ]},
    { id: '2.2', title: 'Coordinate Systems & Fields', leaves: [
      { id: '2.2.1', title: 'Gradient', lessonSlug: '2.2.1' },
      { id: '2.2.2', title: 'Spiral', lessonSlug: '2.2.2' },
      { id: '2.2.3', title: 'Vector Fields', lessonSlug: '2.2.3' },
      { id: '2.2.4', title: 'Distance Fields', lessonSlug: '2.2.4' },
    ]},
    { id: '2.3', title: 'Mathematical Art', leaves: [
      { id: '2.3.1', title: 'Lissajous Curves', lessonSlug: '2.3.1' },
      { id: '2.3.2', title: 'Rose Curves', lessonSlug: '2.3.2' },
      { id: '2.3.3', title: 'Harmonograph Simulation', lessonSlug: '2.3.3' },
      { id: '2.3.4', title: 'Strange Attractors', lessonSlug: '2.3.4' },
    ]},
  ],

  '03': [
    { id: '3.1', title: 'Geometric Transformations', leaves: [
      { id: '3.1.1', title: 'Rotation', lessonSlug: '3.1.1' },
      { id: '3.1.2', title: 'Affine Transformations', lessonSlug: '3.1.2' },
      { id: '3.1.3', title: 'Nonlinear Distortions', lessonSlug: '3.1.3' },
      { id: '3.1.4', title: 'Kaleidoscope Effects', lessonSlug: '3.1.4' },
    ]},
    { id: '3.2', title: 'Masking & Compositing', leaves: [
      { id: '3.2.1', title: 'Mask', lessonSlug: '3.2.1' },
      { id: '3.2.2', title: 'Meme Generator', lessonSlug: '3.2.2' },
      { id: '3.2.3', title: 'Shadow', lessonSlug: '3.2.3' },
      { id: '3.2.4', title: 'Blend Modes', lessonSlug: '3.2.4' },
    ]},
    { id: '3.3', title: 'Artistic Filters', leaves: [
      { id: '3.3.1', title: 'Warhol', lessonSlug: '3.3.1' },
      { id: '3.3.2', title: 'Puzzle (Array Concatenation)', lessonSlug: '3.3.2' },
      { id: '3.3.3', title: 'Hexpanda', lessonSlug: '3.3.3' },
      { id: '3.3.4', title: 'Voronoi Diagrams', lessonSlug: '3.3.4' },
      { id: '3.3.5', title: 'Delaunay Triangulation', lessonSlug: '3.3.5' },
    ]},
    { id: '3.4', title: 'Signal Processing', leaves: [
      { id: '3.4.1', title: 'Convolution', lessonSlug: '3.4.1' },
      { id: '3.4.2', title: 'Edge Detection (Sobel)', lessonSlug: '3.4.2' },
      { id: '3.4.3', title: 'Contour Lines', lessonSlug: '3.4.3' },
      { id: '3.4.4', title: 'Fourier Art', lessonSlug: '3.4.4' },
    ]},
  ],

  '04': [
    { id: '4.1', title: 'Classical Fractals', leaves: [
      { id: '4.1.1', title: 'Fractal Square', lessonSlug: '4.1.1' },
      { id: '4.1.2', title: 'Dragon Curve', lessonSlug: '4.1.2' },
      { id: '4.1.3', title: 'Mandelbrot', lessonSlug: '4.1.3' },
      { id: '4.1.4', title: 'Julia Sets', lessonSlug: '4.1.4' },
      { id: '4.1.5', title: 'Sierpinski', lessonSlug: '4.1.5' },
    ]},
    { id: '4.2', title: 'Natural Fractals', leaves: [
      { id: '4.2.1', title: 'Fractal Trees', lessonSlug: '4.2.1' },
      { id: '4.2.2', title: 'Lightning Bolts', lessonSlug: '4.2.2' },
      { id: '4.2.3', title: 'Fractal Landscapes', lessonSlug: '4.2.3' },
      { id: '4.2.4', title: 'Diffusion-Limited Aggregation', lessonSlug: '4.2.4' },
    ]},
    { id: '4.3', title: 'L-Systems', leaves: [
      { id: '4.3.1', title: 'Plant Generation', lessonSlug: '4.3.1' },
      { id: '4.3.2', title: 'Koch Snowflake', lessonSlug: '4.3.2' },
      { id: '4.3.3', title: 'Penrose Tiling', lessonSlug: '4.3.3' },
    ]},
  ],

  '05': [
    { id: '5.1', title: 'Particle Systems', leaves: [
      { id: '5.1.1', title: 'Sand', lessonSlug: '5.1.1' },
      { id: '5.1.2', title: 'Vortex', lessonSlug: '5.1.2' },
      { id: '5.1.3', title: 'Fireworks Simulation', lessonSlug: '5.1.3' },
      { id: '5.1.4', title: 'Fluid Simulation', lessonSlug: '5.1.4' },
    ]},
    { id: '5.2', title: 'Flocking & Swarms', leaves: [
      { id: '5.2.1', title: 'Boids', lessonSlug: '5.2.1' },
      { id: '5.2.2', title: 'Fish Schooling', lessonSlug: '5.2.2' },
      { id: '5.2.3', title: 'Ant Colony Optimization', lessonSlug: '5.2.3' },
    ]},
    { id: '5.3', title: 'Physics Simulations', leaves: [
      { id: '5.3.1', title: 'Bouncing Ball Animation', lessonSlug: '5.3.1' },
      { id: '5.3.2', title: 'N-Body Planet Simulation', lessonSlug: '5.3.2' },
      { id: '5.3.3', title: 'Double Pendulum Chaos', lessonSlug: '5.3.3' },
      { id: '5.3.4', title: 'Cloth / Rope Simulation', lessonSlug: '5.3.4' },
      { id: '5.3.5', title: 'Magnetic Field Visualization', lessonSlug: '5.3.5' },
    ]},
    { id: '5.4', title: 'Growth & Morphogenesis', leaves: [
      { id: '5.4.1', title: 'Eden Growth Model', lessonSlug: '5.4.1' },
      { id: '5.4.2', title: 'Differential Growth', lessonSlug: '5.4.2' },
      { id: '5.4.3', title: 'Space Colonization', lessonSlug: '5.4.3' },
      { id: '5.4.4', title: 'Turing Patterns', lessonSlug: '5.4.4' },
    ]},
  ],

  '06': [
    { id: '6.1', title: 'Noise Functions', leaves: [
      { id: '6.1.1', title: 'Perlin Noise', lessonSlug: '6.1.1' },
      { id: '6.1.2', title: 'Simplex Noise', lessonSlug: '6.1.2' },
      { id: '6.1.3', title: 'Worley Noise', lessonSlug: '6.1.3' },
      { id: '6.1.4', title: 'Colored Noise', lessonSlug: '6.1.4' },
    ]},
    { id: '6.2', title: 'Terrain Generation', leaves: [
      { id: '6.2.1', title: 'Height Maps', lessonSlug: '6.2.1' },
      { id: '6.2.2', title: 'Erosion Simulation', lessonSlug: '6.2.2' },
      { id: '6.2.3', title: 'Cave Generation', lessonSlug: '6.2.3' },
      { id: '6.2.4', title: 'Island Generation', lessonSlug: '6.2.4' },
    ]},
    { id: '6.3', title: 'Texture Synthesis', leaves: [
      { id: '6.3.1', title: 'Marble & Wood', lessonSlug: '6.3.1' },
      { id: '6.3.2', title: 'Cloud Generation', lessonSlug: '6.3.2' },
      { id: '6.3.3', title: 'Abstract Patterns', lessonSlug: '6.3.3' },
      { id: '6.3.4', title: 'Procedural Materials', lessonSlug: '6.3.4' },
    ]},
    { id: '6.4', title: 'Wave & Interference Patterns', leaves: [
      { id: '6.4.1', title: 'Moiré Patterns', lessonSlug: '6.4.1' },
      { id: '6.4.2', title: 'Wave Interference', lessonSlug: '6.4.2' },
      { id: '6.4.3', title: 'Cymatics', lessonSlug: '6.4.3' },
    ]},
  ],

  '07': [
    { id: '7.1', title: 'Clustering & Segmentation', leaves: [
      { id: '7.1.1', title: 'K-Means Clustering', lessonSlug: '7.1.1' },
      { id: '7.1.2', title: 'Mean-Shift Segmentation', lessonSlug: '7.1.2' },
      { id: '7.1.3', title: 'DBSCAN Pattern Detection', lessonSlug: '7.1.3' },
    ]},
    { id: '7.2', title: 'Classification & Recognition', leaves: [
      { id: '7.2.1', title: 'Decision Tree Classifier', lessonSlug: '7.2.1' },
      { id: '7.2.2', title: 'Random Forests', lessonSlug: '7.2.2' },
      { id: '7.2.3', title: 'SVM Style Detection', lessonSlug: '7.2.3' },
    ]},
    { id: '7.3', title: 'Dimensionality Reduction', leaves: [
      { id: '7.3.1', title: 'PCA Color Palette', lessonSlug: '7.3.1' },
      { id: '7.3.2', title: 't-SNE Visualization', lessonSlug: '7.3.2' },
      { id: '7.3.3', title: 'UMAP Visualizations', lessonSlug: '7.3.3' },
    ]},
    { id: '7.4', title: 'Statistical Methods', leaves: [
      { id: '7.4.1', title: 'Monte Carlo Sampling', lessonSlug: '7.4.1' },
      { id: '7.4.2', title: 'Markov Chains', lessonSlug: '7.4.2' },
      { id: '7.4.3', title: 'Hidden Markov Models', lessonSlug: '7.4.3' },
    ]},
  ],

  '08': [
    { id: '8.1', title: 'Animation Fundamentals', leaves: [
      { id: '8.1.1', title: 'Image Transformations', lessonSlug: '8.1.1' },
      { id: '8.1.2', title: 'Easing Functions', lessonSlug: '8.1.2' },
      { id: '8.1.3', title: 'Interpolation Techniques', lessonSlug: '8.1.3' },
      { id: '8.1.4', title: 'Sprite Sheets', lessonSlug: '8.1.4' },
    ]},
    { id: '8.2', title: 'Organic Motion', leaves: [
      { id: '8.2.1', title: 'Flower Assembly', lessonSlug: '8.2.1' },
      { id: '8.2.2', title: 'Infinite Blossom', lessonSlug: '8.2.2' },
      { id: '8.2.3', title: 'Walk Cycles', lessonSlug: '8.2.3' },
      { id: '8.2.4', title: 'Breathing / Pulsing', lessonSlug: '8.2.4' },
    ]},
    { id: '8.3', title: 'Cinematic Effects', leaves: [
      { id: '8.3.1', title: 'Star Wars Titles', lessonSlug: '8.3.1' },
      { id: '8.3.2', title: 'Thank You', lessonSlug: '8.3.2' },
      { id: '8.3.3', title: 'Particle Text Reveals', lessonSlug: '8.3.3' },
      { id: '8.3.4', title: 'Morphing Transitions', lessonSlug: '8.3.4' },
    ]},
    { id: '8.4', title: 'Generative Animation', leaves: [
      { id: '8.4.1', title: 'Music Visualization', lessonSlug: '8.4.1' },
      { id: '8.4.2', title: 'Data-Driven Animation', lessonSlug: '8.4.2' },
      { id: '8.4.3', title: 'Animated Fractals', lessonSlug: '8.4.3' },
    ]},
  ],

  '09': [
    { id: '9.1', title: 'Neural Network Fundamentals', leaves: [
      { id: '9.1.1', title: 'Perceptron from Scratch', lessonSlug: '9.1.1' },
      { id: '9.1.2', title: 'Backpropagation Visualization', lessonSlug: '9.1.2' },
      { id: '9.1.3', title: 'Activation Functions Art', lessonSlug: '9.1.3' },
    ]},
    { id: '9.2', title: 'Network Architectures', leaves: [
      { id: '9.2.1', title: 'Feedforward Networks', lessonSlug: '9.2.1' },
      { id: '9.2.2', title: 'Convolutional Networks', lessonSlug: '9.2.2' },
      { id: '9.2.3', title: 'Recurrent Networks', lessonSlug: '9.2.3' },
    ]},
    { id: '9.3', title: 'Training Dynamics', leaves: [
      { id: '9.3.1', title: 'Loss Landscape', lessonSlug: '9.3.1' },
      { id: '9.3.2', title: 'Gradient Descent Animation', lessonSlug: '9.3.2' },
      { id: '9.3.3', title: 'Overfitting / Underfitting', lessonSlug: '9.3.3' },
    ]},
    { id: '9.4', title: 'Feature Visualization', leaves: [
      { id: '9.4.1', title: 'DeepDream', lessonSlug: '9.4.1' },
      { id: '9.4.2', title: 'Feature Map Art', lessonSlug: '9.4.2' },
      { id: '9.4.3', title: 'Network Attention', lessonSlug: '9.4.3' },
    ]},
  ],

  '10': [
    { id: '10.1', title: 'TD Environment & Workflow', leaves: [
      { id: '10.1.1', title: 'Node Networks', lessonSlug: '10.1.1' },
      { id: '10.1.2', title: 'Python Integration Basics', lessonSlug: '10.1.2' },
      { id: '10.1.3', title: 'Performance Monitoring', lessonSlug: '10.1.3' },
    ]},
    { id: '10.2', title: 'Recreating Static Exercises', leaves: [
      { id: '10.2.1', title: 'Core Exercises Realtime', lessonSlug: '10.2.1' },
      { id: '10.2.2', title: 'Boids in TouchDesigner', lessonSlug: '10.2.2' },
      { id: '10.2.3', title: 'Planet Simulation TD', lessonSlug: '10.2.3' },
      { id: '10.2.4', title: 'Fractals Realtime', lessonSlug: '10.2.4' },
    ]},
    { id: '10.3', title: 'NumPy ↔ TD Pipeline', leaves: [
      { id: '10.3.1', title: 'Script Operators', lessonSlug: '10.3.1' },
      { id: '10.3.2', title: 'Array Processing', lessonSlug: '10.3.2' },
      { id: '10.3.3', title: 'Custom Components', lessonSlug: '10.3.3' },
    ]},
    { id: '10.4', title: 'Interactive Controls', leaves: [
      { id: '10.4.1', title: 'UI Building', lessonSlug: '10.4.1' },
      { id: '10.4.2', title: 'Parameter Mapping', lessonSlug: '10.4.2' },
      { id: '10.4.3', title: 'Preset Systems', lessonSlug: '10.4.3' },
    ]},
  ],

  '11': [
    { id: '11.1', title: 'Input Devices', leaves: [
      { id: '11.1.1', title: 'Webcam Processing', lessonSlug: '11.1.1' },
      { id: '11.1.2', title: 'Audio Reactivity', lessonSlug: '11.1.2' },
      { id: '11.1.3', title: 'MIDI / OSC Control', lessonSlug: '11.1.3' },
      { id: '11.1.4', title: 'Kinect / Leap Motion', lessonSlug: '11.1.4' },
    ]},
    { id: '11.2', title: 'Computer Vision in TD', leaves: [
      { id: '11.2.1', title: 'Motion Detection', lessonSlug: '11.2.1' },
      { id: '11.2.2', title: 'Blob Tracking', lessonSlug: '11.2.2' },
      { id: '11.2.3', title: 'Face Detection', lessonSlug: '11.2.3' },
      { id: '11.2.4', title: 'Optical Flow', lessonSlug: '11.2.4' },
    ]},
    { id: '11.3', title: 'Physical Computing', leaves: [
      { id: '11.3.1', title: 'Arduino Integration', lessonSlug: '11.3.1' },
      { id: '11.3.2', title: 'DMX Lighting Control', lessonSlug: '11.3.2' },
      { id: '11.3.3', title: 'Projection Mapping', lessonSlug: '11.3.3' },
    ]},
    { id: '11.4', title: 'Network Communication', leaves: [
      { id: '11.4.1', title: 'Multi-Machine Setups', lessonSlug: '11.4.1' },
      { id: '11.4.2', title: 'WebSocket / WebRTC', lessonSlug: '11.4.2' },
      { id: '11.4.3', title: 'Remote Control Interfaces', lessonSlug: '11.4.3' },
    ]},
  ],

  '12': [
    { id: '12.1', title: 'Generative Adversarial Networks', leaves: [
      { id: '12.1.1', title: 'GAN Architecture', lessonSlug: '12.1.1' },
      { id: '12.1.2', title: 'DCGAN Art', lessonSlug: '12.1.2' },
      { id: '12.1.3', title: 'StyleGAN Exploration', lessonSlug: '12.1.3' },
      { id: '12.1.4', title: 'Pix2Pix Applications', lessonSlug: '12.1.4' },
    ]},
    { id: '12.2', title: 'Variational Autoencoders', leaves: [
      { id: '12.2.1', title: 'Latent Space Exploration', lessonSlug: '12.2.1' },
      { id: '12.2.2', title: 'Interpolation Animations', lessonSlug: '12.2.2' },
      { id: '12.2.3', title: 'Conditional VAEs', lessonSlug: '12.2.3' },
    ]},
    { id: '12.3', title: 'Diffusion Models', leaves: [
      { id: '12.3.1', title: 'DDPM Basics', lessonSlug: '12.3.1' },
      { id: '12.3.2', title: 'ControlNet Guided Generation', lessonSlug: '12.3.2' },
    ]},
    { id: '12.4', title: 'Bridging Paradigms', leaves: [
      { id: '12.4.1', title: 'Neural Style Transfer', lessonSlug: '12.4.1' },
      { id: '12.4.2', title: 'VQ-VAE & VQ-GAN', lessonSlug: '12.4.2' },
    ]},
    { id: '12.5', title: 'Personalization & Efficiency', leaves: [
      { id: '12.5.1', title: 'DreamBooth Personalization', lessonSlug: '12.5.1' },
    ]},
    { id: '12.6', title: 'Transformer Generation', leaves: [
      { id: '12.6.1', title: 'Taming Transformers', lessonSlug: '12.6.1' },
      { id: '12.6.2', title: 'Diffusion Transformer (DiT)', lessonSlug: '12.6.2' },
    ]},
    { id: '12.7', title: 'Modern Frontiers', leaves: [
      { id: '12.7.1', title: 'Flow Matching', lessonSlug: '12.7.1' },
    ]},
  ],

  '13': [
    { id: '13.1', title: 'ML Models in TD', leaves: [
      { id: '13.1.1', title: 'MediaPipe Integration', lessonSlug: '13.1.1' },
      { id: '13.1.2', title: 'RunwayML Bridge', lessonSlug: '13.1.2' },
      { id: '13.1.3', title: 'ONNX Runtime', lessonSlug: '13.1.3' },
    ]},
    { id: '13.2', title: 'Real-time AI Effects', leaves: [
      { id: '13.2.1', title: 'Style Transfer Live', lessonSlug: '13.2.1' },
      { id: '13.2.2', title: 'Realtime Segmentation', lessonSlug: '13.2.2' },
      { id: '13.2.3', title: 'Pose-Driven Effects', lessonSlug: '13.2.3' },
    ]},
    { id: '13.3', title: 'Generative Models Live', leaves: [
      { id: '13.3.1', title: 'GAN Inference Optimization', lessonSlug: '13.3.1' },
      { id: '13.3.2', title: 'Latent Space Navigation UI', lessonSlug: '13.3.2' },
      { id: '13.3.3', title: 'Model Switching Systems', lessonSlug: '13.3.3' },
    ]},
    { id: '13.4', title: 'Hybrid Pipelines', leaves: [
      { id: '13.4.1', title: 'Preprocessing in TD', lessonSlug: '13.4.1' },
      { id: '13.4.2', title: 'Python ML Processing', lessonSlug: '13.4.2' },
      { id: '13.4.3', title: 'Post-Processing Chains', lessonSlug: '13.4.3' },
    ]},
  ],

  '14': [
    { id: '14.1', title: 'Data Sources', leaves: [
      { id: '14.1.1', title: 'APIs & Data Scraping', lessonSlug: '14.1.1' },
      { id: '14.1.2', title: 'Sensor Networks', lessonSlug: '14.1.2' },
      { id: '14.1.3', title: 'Social Media Streams', lessonSlug: '14.1.3' },
      { id: '14.1.4', title: 'Environmental Data', lessonSlug: '14.1.4' },
    ]},
    { id: '14.2', title: 'Visualization Techniques', leaves: [
      { id: '14.2.1', title: 'Network Graphs', lessonSlug: '14.2.1' },
      { id: '14.2.2', title: 'Flow Visualization', lessonSlug: '14.2.2' },
      { id: '14.2.3', title: 'Multidimensional Scaling', lessonSlug: '14.2.3' },
      { id: '14.2.4', title: 'Time Series Art', lessonSlug: '14.2.4' },
    ]},
    { id: '14.3', title: 'Sonification', leaves: [
      { id: '14.3.1', title: 'Data to Sound Mapping', lessonSlug: '14.3.1' },
      { id: '14.3.2', title: 'Granular Synthesis', lessonSlug: '14.3.2' },
      { id: '14.3.3', title: 'Rhythmic Patterns', lessonSlug: '14.3.3' },
    ]},
    { id: '14.4', title: 'Physical Data Sculptures', leaves: [
      { id: '14.4.1', title: '3D Printing Preparation', lessonSlug: '14.4.1' },
      { id: '14.4.2', title: 'Laser Cutting Patterns', lessonSlug: '14.4.2' },
      { id: '14.4.3', title: 'CNC Toolpaths', lessonSlug: '14.4.3' },
    ]},
  ],

  '15': [
    { id: '15', title: 'Synthesis Project', leaves: [
      { id: '15', title: 'Eternal Flow — capstone', lessonSlug: '15' },
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

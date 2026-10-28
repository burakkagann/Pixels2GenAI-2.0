/**
 * Module covers on the home curriculum (MC3, approved 28 Oct 2026): each
 * module's best real lesson output, reprinted as a one-ink riso print in its
 * path colour. Images are 480 x 300 WebP in public/curriculum-covers/, made
 * from workshop-planning/review/curriculum-covers-2026-10-28/render_covers.py.
 * Modules without a live lesson (00, 07, 13, 14, 15) have no entry: they show
 * their planned sub-topics as type instead of a picture.
 */
export interface ModuleCover {
  src: string;
  width: number;
  height: number;
  alt: string;
}

const cover = (idx: string, alt: string): ModuleCover => ({
  src: `/curriculum-covers/m${idx}.webp`,
  width: 480,
  height: 300,
  alt,
});

export const COVERS: Record<string, ModuleCover> = {
  '01': cover('01', 'Riso print of the Richter-style random colour grid from lesson 1.2.1'),
  '02': cover('02', 'Riso print of the harmonograph curve from lesson 2.3.3'),
  '03': cover('03', 'Riso print of the swirl distortion from lesson 3.1.3'),
  '04': cover('04', 'Riso print of the zoomed Mandelbrot set from lesson 4.1.3'),
  '05': cover('05', 'Riso print of the double pendulum trace from lesson 5.3.3'),
  '06': cover('06', 'Riso print of the Perlin noise clouds from lesson 6.1.1'),
  '08': cover('08', 'Riso print of the infinite blossom still from lesson 8.2.2'),
  '09': cover('09', 'Riso print of the convolutional feature maps from lesson 9.2.2'),
  '10': cover('10', 'Riso print of the TouchDesigner node network output from lesson 10.1.1'),
  '11': cover('11', 'Riso print of the face triangulation from lesson 11.2.3'),
  '12': cover('12', 'Riso print of the DreamBooth style grid from lesson 12.5.1'),
};

/** Short forms of the planned sub-topics (subtopics.ts) for the modules that
 *  have no live lesson yet, sized to fit the 16:10 tile. */
export const PLANNED_TOPICS: Record<string, string[]> = {
  '00': ['What is generative art', 'AI, ML, algorithms', 'Setup'],
  '07': ['Clustering', 'Classification', 'Dimensionality reduction', 'Statistics'],
  '13': ['ML models in TD', 'Real-time AI effects', 'Generative models live', 'Hybrid pipelines'],
  '14': ['Data sources', 'Visualisation', 'Sonification', 'Data sculptures'],
  '15': ['Your own piece', 'built from all three paths'],
};

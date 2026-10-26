// Resolved by the workshopArea integration (src/integrations/workshop-area.mjs):
// src/components/workshops/brand/ when PUBLIC_WORKSHOP_SERIES=true, else the
// pre-series markup in src/components/workshops/classic/.
declare module 'p2g:workshop-brand/Hero.astro' {
  const Hero: typeof import('./components/workshops/brand/Hero.astro').default;
  export default Hero;
}
declare module 'p2g:workshop-brand/Series.astro' {
  const Series: typeof import('./components/workshops/brand/Series.astro').default;
  export default Series;
}
declare module 'p2g:workshop-brand/Pilot.astro' {
  const Pilot: typeof import('./components/workshops/brand/Pilot.astro').default;
  export default Pilot;
}

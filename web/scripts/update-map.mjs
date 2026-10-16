// Pinned public-domain Natural Earth geometry; run from web/ with node scripts/update-map.mjs.
import {createHash} from 'node:crypto';
import {mkdir, writeFile} from 'node:fs/promises';
import {geoArea} from 'd3-geo';
const revision = '9380cca83db5f9aef52d5e762765100745f84b27';
const url = `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/${revision}/geojson/ne_110m_admin_0_countries.geojson`;
const response = await fetch(url);
if (!response.ok) throw new Error(`Natural Earth download: ${response.status}`);
const bytes = Buffer.from(await response.arrayBuffer());
if (createHash('sha256').update(bytes).digest('hex') !== '6866c877d39cba9c357620878839b336d569f8c662d3cfab4cb1dbe2d39c977f') throw new Error('Source checksum mismatch');
const source = JSON.parse(bytes.toString());
const round = coordinates => coordinates.map(value => Array.isArray(value) ? round(value) : Math.round(value * 1000) / 1000);
const features = source.features.map(feature => {
  const p = feature.properties;
  const geometry = {...feature.geometry, coordinates: round(feature.geometry.coordinates)};
  if (geoArea(geometry) > 2 * Math.PI) {
    const polygons = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
    polygons.forEach(polygon => polygon.forEach(ring => ring.reverse()));
  }
  return {type:'Feature', id:p.ADM0_A3.toLowerCase(), properties:{name:p.NAME_EN, center:[p.LABEL_X,p.LABEL_Y]}, geometry};
});
if (features.length !== 177 || new Set(features.map(f=>f.id)).size !== 177) throw new Error('Unexpected country identities');
await mkdir('src/data', {recursive:true});
await writeFile('src/data/countries.json', JSON.stringify({type:'FeatureCollection',features})+'\n');
console.log(`Generated ${features.length} country geometries from ${revision}`);

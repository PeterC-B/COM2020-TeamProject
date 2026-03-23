import type { LayerSpecification } from 'maplibre-gl'

type LayerOf<T extends LayerSpecification['type']> = Extract<LayerSpecification, { type: T }>
type BackgroundLayer = LayerOf<'background'>
type CircleLayer = LayerOf<'circle'>
type FillLayer = LayerOf<'fill'>
type HeatmapLayer = LayerOf<'heatmap'>
type HillshadeLayer = LayerOf<'hillshade'>
type LineLayer = LayerOf<'line'>
type RasterLayer = LayerOf<'raster'>
type SymbolLayer = LayerOf<'symbol'>

export type MapLayer =
    | LineLayer
    | CircleLayer
    | FillLayer
    | SymbolLayer
    | HeatmapLayer
    | RasterLayer
    | HillshadeLayer
    | BackgroundLayer

// Base road styling.
export const EDGE_BASE_LAYER: LineLayer = {
    id: 'edges-line',
    type: 'line',
    source: 'edges',
    paint: {
        'line-color': '#1f4e5f',
        'line-width': 2,
        'line-opacity': 0.0001,
    },
}

// Highlighted road for a single selected edge.
export const EDGE_HIGHLIGHT_LAYER: LineLayer = {
    id: 'edges-line-highlight',
    type: 'line',
    source: 'edges',
    filter: ['==', ['get', 'edge_id'], -1],
    paint: {
        'line-color': '#ff9f1c',
        'line-width': 4,
        'line-opacity': 0.95,
    },
}

// Increased the size of the hit area to make edges easier to click.
export const EDGE_HIT_LAYER: LineLayer = {
    id: 'edges-line-hit',
    type: 'line',
    source: 'edges',
    paint: {
        'line-color': '#000000',
        'line-width': 12,
        'line-opacity': 0,
    },
}

// Base node styling.
export const NODE_BASE_LAYER: CircleLayer = {
    id: 'nodes-circle',
    type: 'circle',
    source: 'nodes',
    paint: {
        'circle-color': '#d96f2b',
        'circle-radius': 3,
        'circle-stroke-color': '#0b1f26',
        'circle-stroke-width': 1,
    },
}

// Highlighted node for a single selected node.
export const NODE_HIGHLIGHT_LAYER: CircleLayer = {
    id: 'nodes-circle-highlight',
    type: 'circle',
    source: 'nodes',
    filter: ['==', ['get', 'node_id'], -1],
    paint: {
        'circle-color': '#ffe66d',
        'circle-radius': 6,
        'circle-stroke-color': '#0b1f26',
        'circle-stroke-width': 2,
    },
}

// Increased the size of the hit area to make nodes easier to click.
export const NODE_HIT_LAYER: CircleLayer = {
    id: 'nodes-circle-hit',
    type: 'circle',
    source: 'nodes',
    paint: {
        'circle-color': '#000000',
        'circle-radius': 10,
        'circle-opacity': 0,
    },
}
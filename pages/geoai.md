---
title: "GeoAI"
summary: "Environmental AI research using satellite imagery, computer vision, and responsible machine learning."
slug: geoai
---

# GeoAI

The GeoAI project explores whether AI models can help identify and monitor stages of coastal dune succession from satellite imagery.

The first focus is coastal sand dune ecosystems and psammosere succession: the gradual process where pioneer plants stabilise mobile sand and allow more complex ecosystems to develop over time. These systems are important for biodiversity, ecological resilience, and natural coastal protection.

More broadly, this work is about learning how environmental AI systems can be built responsibly. Environmental monitoring increasingly depends on machine learning and large datasets, but questions around data integrity, dataset provenance, and model robustness are not always treated as central.

The guiding principle is simple: use AI with care, ethics, and a moral compass. The goal is not just to make models work, but to understand when they should be trusted, where they might fail, and how to design systems that are transparent, secure, and useful.

## Current direction

- collect and organise satellite imagery of dune systems
- define visual indicators for vegetation cover and succession stage
- test simple computer vision baselines
- compare ecosystem change over time
- detect loss or recovery of vegetation
- document dataset sources and assumptions
- think about data integrity and model robustness from the start
- connect technical experiments to ethical questions around trust, bias, and impact

## Longer-term ideas

The same approach could eventually be extended to wetlands, reforestation monitoring, and other ecosystem restoration contexts.

The aim is not just to build a model, but to understand what environmental AI systems can reliably detect, where they fail, and how to make them more trustworthy.

## Repository

The project repository is available here:

[stoodlesz/dune-ai-monitoring](https://github.com/stoodlesz/dune-ai-monitoring)

The repo includes early work on dataset manifests, provenance and integrity metadata, Sentinel-2 imagery, Microsoft Planetary Computer helpers, NDVI and NDWI calculations, image tiling, psammosere labels, and secure ML pipeline planning.

=> [See all projects](project.html)

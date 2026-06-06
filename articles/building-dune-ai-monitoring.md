---
title: "Building a first GeoAI pipeline for monitoring sand dune ecosystems"
date: 2026-06-06
summary: "A detailed process note on starting my dune-ai-monitoring project: why sand dunes matter, how the repository was structured, and why provenance and secure ML belong in environmental AI."
slug: building-dune-ai-monitoring
---

# Building a first GeoAI pipeline for monitoring sand dune ecosystems

On 5 June 2026, I started turning a long-running interest into an actual research project.

The project is called [dune-ai-monitoring](https://github.com/stoodlesz/dune-ai-monitoring), and the idea is to explore how machine learning, computer vision, and remote sensing could be used to analyse coastal sand dune ecosystems, especially psammoseres.

This article is partly a project log and partly a research note. I want to document what I built first, why I built it in that order, and why I think sand dunes are a genuinely important subject for environmental AI.

## Why sand dunes?

Sand dunes can look simple from a distance, but they are complex ecological systems.

They are shaped by wind, vegetation, sediment movement, erosion, human pressure, and climate conditions. They also go through ecological succession. In a psammosere, pioneer plants begin stabilising mobile sand, which allows more complex plant communities to develop over time. That progression can include embryo dunes, yellow dunes, grey dunes, mature dune grassland, and eventually dune scrub or woodland.

That ecological story is what first made dunes interesting to me.

But dunes are not just interesting biologically. They matter practically. The European Climate, Infrastructure and Environment Executive Agency notes that sand dunes provide habitat for rare plants and wildlife, while also helping protect against erosion, flooding, and storm damage. The same article also points out that many dunes are being damaged, especially because so many people live near or use coastal areas.

That makes dune monitoring a good environmental AI problem:

- dunes are ecologically important
- they change over time
- they can be observed from above
- they include visible patterns of sand, vegetation, water, and human disturbance
- they need restoration and management decisions that should not be based on guesswork alone

If satellite imagery can help track vegetation recovery, dune degradation, or restoration progress, then AI could become useful as a supporting tool for conservation.

But the word "supporting" matters. AI should support environmental monitoring, not replace ecological expertise.

## The research idea

The long-term goal is to build models that can help detect dune ecosystem stages, identify degradation, and eventually support restoration planning from imagery.

The first research goals in the repository are:

- detect psammosere stages from aerial or satellite imagery
- track ecological change across time
- predict dune degradation or restoration
- experiment with AI-assisted ecological restoration scenarios
- build secure ML pipelines that are resistant to data poisoning or adversarial manipulation

That last point is important to me.

I do not want this to be only an environmental computer vision project. I want it to also treat environmental AI as a security and trust problem. If environmental monitoring systems start influencing conservation policy, land management, or restoration funding, then the data pipeline has to be traceable and robust.

It should be possible to ask:

- where did this image come from?
- when was it captured?
- what sensor and bands were used?
- how was it labelled?
- how confident is the label?
- has the file changed since it was registered?
- could the model be misled by bad data, weak labels, or manipulated imagery?

That is why the first day of the project was not about training a model.

It was about building the foundations.

## Step 1: creating the repository structure

The first thing I set up was a project repository with a structure that could grow into a proper research codebase.

The repository includes:

- `README.md` for the project overview
- `ROADMAP.md` for research phases
- `SECURITY.md` for secure ML considerations
- `pyproject.toml` and `requirements.txt` for package setup
- `data/` for raw, processed, and metadata files
- `docs/` for documentation
- `journal/` for project logs
- `notebooks/` for exploration
- `research/` for literature notes
- `src/dune_ai_monitoring/` for reusable code
- `tests/` for validation

This might seem like admin, but it matters.

Research projects become hard to continue when everything is mixed together: notebooks, downloaded files, experimental scripts, notes, and outputs all in one folder. I wanted the project to be understandable when I came back to it later.

The structure also helps separate the different kinds of work:

- research notes are not the same as code
- raw imagery is not the same as processed training data
- metadata is not optional
- tests should exist before the project becomes too large to reason about

This is the part of research that feels boring until it saves you.

## Step 2: defining the roadmap

I then wrote a roadmap so the project had a clear direction.

The roadmap breaks the work into five phases.

The first phase is project foundations: identifying datasets, building preprocessing pipelines, and defining labels for dune succession stages.

The second phase is psammosere classification. This is where the project would train models to classify stages such as embryo dunes, yellow dunes, grey dunes, mature dune grassland, and dune scrub or woodland.

The third phase is temporal ecosystem change detection. This would use imagery across time to detect vegetation loss, dune erosion, or recovery.

The fourth phase is predictive environmental modelling. This is the more speculative part: could models help simulate restoration scenarios, vegetation spread, or dune stabilisation?

The fifth phase is environmental AI security. This is where the project asks whether environmental ML systems can be manipulated through adversarial imagery, synthetic imagery, or dataset poisoning.

Writing the roadmap helped me keep the project from becoming a vague "AI for dunes" idea.

It became a staged research pipeline.

## Step 3: starting with provenance, not modelling

The most important early design choice was to build a dataset manifest before building the model.

The dataset manifest is a CSV-based record of each image. It tracks where an image came from, how it is labelled, and whether its bytes can be verified later.

The manifest includes fields such as:

- image path
- source name
- source URL
- capture date
- location name
- latitude and longitude
- sensor
- bands
- psammosere stage
- label source
- label confidence
- SHA-256 hash
- licence
- notes

This connects the environmental research side of the project to the cybersecurity side.

For example, the `sha256` field means a downloaded image can be checked later to see whether it has changed. The `source_url` field keeps the dataset traceable. The `label_source` and `label_confidence` fields make it possible to distinguish between a high-confidence field-survey label and a weaker label produced through manual review or derived from land cover.

This matters because environmental AI models are only as trustworthy as their data.

If I eventually train a classifier to identify dune succession stages, I need to know what imagery was used, where it came from, and how the labels were produced. Without that, the model might look scientific while being impossible to audit.

## Step 4: building the first reusable code

The first reusable code modules live under `src/dune_ai_monitoring/`.

The early package includes:

- dataset manifest helpers
- CSV loading and writing
- manifest validation
- SHA-256 hashing
- image tiling helpers
- NDVI and NDWI calculations
- psammosere stage label validation

The preprocessing pieces are important because raw satellite imagery is not automatically model-ready.

Images may need to be tiled into smaller patches. Spectral indices such as NDVI can help estimate vegetation patterns. Labels need to be consistent. Metadata needs to travel with the imagery.

At this stage, the project is still foundational. It does not yet train a model. But it creates the basic tools that will make model training less chaotic later.

## Step 5: adding a command-line tool for image registration

The next useful step was creating `dune-manifest-add`.

This command registers a local image in the manifest. It records the metadata, computes the file's SHA-256 hash, and writes the row into a manifest CSV.

That means an image can be added to the dataset in a repeatable way, rather than manually copying details into a spreadsheet and hoping nothing gets missed.

In practical terms, this command helps answer:

- what is this image?
- where did it come from?
- what location does it represent?
- what label does it currently have?
- how confident is that label?
- can I verify the file later?

This is the kind of thing I want to build into the project from the beginning, because retrofitting provenance later is painful.

## Step 6: connecting to real satellite imagery

After the manifest tooling, the next layer was `dune-pc-download`.

This command searches Microsoft Planetary Computer's STAC API for Sentinel-2 L2A imagery. It can select a low-cloud-cover item, download a chosen asset, compute its SHA-256 hash, register it in the manifest, and optionally write a readable report.

This was the point where the project moved from "how should imagery be stored?" to "how can I start bringing real satellite imagery into the pipeline?"

The command supports downloading a true-colour visual asset or individual spectral bands such as `B02`, `B03`, `B04`, or `B08`. Those individual bands will matter later for vegetation index work, including NDVI.

## Step 7: first real site test with Dune du Pilat

The first real test used Dune du Pilat in France.

The downloader selected a Sentinel-2 item from 2025-07-11 with very low cloud cover. A small rendered preview image was downloaded locally for inspection. The image itself was kept out of Git, but the metadata record and readable report were added under `data/metadata/`.

The report included:

- source item ID
- capture date
- cloud cover
- SHA-256 hash
- bounding box
- approximate search-box area
- a note that the search-box area is not yet a measured sand-dune area

That last point is important.

At this stage, the project can record the approximate area of the search box, but it cannot yet measure the actual area of sand dunes. That will require later image analysis to separate sand, vegetation, water, and built-up pixels.

This is the kind of distinction I want the project to keep making: what the data says, what it does not say yet, and what work is still needed before a claim becomes meaningful.

## Step 8: writing the security notes

The repository also includes a `SECURITY.md` file.

This felt necessary because environmental AI is often discussed as if the main problem is model performance. But performance is only one part of trust.

The security notes identify three broad risks:

- adversarial imagery
- dataset poisoning
- model misuse

Adversarial imagery could include manipulated satellite imagery, synthetic aerial imagery, or perturbations designed to mislead a model.

Dataset poisoning could involve incorrect ecosystem labels, corrupted datasets, or deliberately manipulated training examples.

Model misuse could happen if a model is used outside its geographic training range, treated as ground truth, or relied on without field validation.

The secure ML practices I want to build around this include:

- reproducible datasets
- transparent preprocessing pipelines
- adversarial robustness testing
- experiment tracking
- dataset provenance documentation

This is where the project connects back to my broader interest in cybersecurity and responsible AI.

## Step 9: keeping a project journal

I also added a journal entry for 5 June 2026.

The point of the journal is to record the process while the project is still fresh. It captures what changed, what the codebase can do, what it cannot do yet, and what the next useful step might be.

The first journal entry records that the project can now:

- search for Sentinel-2 imagery
- download a preview asset
- register the downloaded file in a provenance-aware manifest
- compute a SHA-256 hash
- generate a human-readable image report
- keep source imagery out of Git while preserving metadata

It also records what the project cannot do yet:

- it does not yet train a model
- it does not yet calculate the actual area of sand dunes
- it does not yet separate sand, vegetation, water, and urban pixels

That honesty is useful.

It stops the project from becoming overclaimed too early.

## Why tracking dunes matters

The importance of sand dunes is not only local or aesthetic.

Coastal dunes can act as natural protective systems. They absorb and buffer some of the pressure from erosion, flooding, and storm damage. They also support rare plants, wildlife, and specialised habitats.

European restoration work already treats dunes as important ecological infrastructure. CINEA describes LIFE projects restoring dunes through grazing, invasive species removal, wet dune slack restoration, bare sand creation, and habitat management. Climate-ADAPT also frames dune construction and strengthening as a nature-based adaptation option for coastal resilience.

That makes monitoring important.

If dunes are restored, managers need to know whether vegetation is recovering. If dunes are degrading, they need to detect where and when change is happening. If invasive species are spreading, or bare sand is disappearing, or vegetation patterns are shifting, then remote sensing may help create a broader picture than field visits alone.

The challenge is that satellite imagery does not interpret itself.

That is where AI might help, but only if the pipeline is careful.

## What comes next

The next practical step is to build preprocessing outputs from recorded source imagery.

That means taking a registered image and beginning to separate meaningful land-cover patterns:

- sand
- vegetation
- water
- built-up or urban pixels

From there, the project can begin exploring psammosere classification categories and testing simple baselines.

The longer-term path is:

- collect labelled dune imagery datasets
- train a psammosere stage classifier
- analyse satellite and aerial imagery
- detect ecosystem change across time
- evaluate adversarial robustness of environmental ML models
- explore whether the same approach could support wetlands, reforestation, floodplain ecosystems, or broader habitat restoration

The project is still early.

But it now has a foundation: a repository, a roadmap, a security framing, a dataset manifest, first preprocessing utilities, a satellite imagery downloader, and a journal of what has been done.

That feels like the right first step.

## References

- CINEA (2021). [Strengthening Europe's sand dunes](https://cinea.ec.europa.eu/news-events/news/strengthening-europes-sand-dunes-2021-06-23_en).
- Climate-ADAPT (2023). [Dune construction and strengthening](https://climate-adapt.eea.europa.eu/en/metadata/adaptation-options/dune-construction-and-strengthening).
- Williams, S. (2026). [Dune AI Monitoring repository](https://github.com/stoodlesz/dune-ai-monitoring).
- Williams, S. (2026). [Dune AI Monitoring roadmap](https://github.com/stoodlesz/dune-ai-monitoring/blob/main/ROADMAP.md).
- Williams, S. (2026). [Dune AI Monitoring security considerations](https://github.com/stoodlesz/dune-ai-monitoring/blob/main/SECURITY.md).
- Williams, S. (2026). [Dataset manifest documentation](https://github.com/stoodlesz/dune-ai-monitoring/blob/main/docs/dataset_manifest.md).
- Williams, S. (2026). [Project journal, 5 June 2026](https://github.com/stoodlesz/dune-ai-monitoring/blob/main/journal/2026-06-05.md).
- Williams, S. (2026). [Research literature notes](https://github.com/stoodlesz/dune-ai-monitoring/blob/main/research/literature.md).

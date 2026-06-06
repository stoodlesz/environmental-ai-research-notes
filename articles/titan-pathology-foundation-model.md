---
title: "TITAN and the promise of whole-slide pathology foundation models"
date: 2026-06-06
summary: "A clear breakdown of TITAN, a multimodal whole-slide foundation model for pathology, and what it raises about provenance, auditability, governance, and interpretability."
slug: titan-pathology-foundation-model
---

# TITAN and the promise of whole-slide pathology foundation models

This is a working research note on Ding et al., "A multimodal whole-slide foundation model for pathology", published in Nature Medicine in 2025.

The paper introduces TITAN, a multimodal foundation model for computational pathology. Its central claim is that pathology AI should move beyond patch-level representations and toward slide-level models that can understand whole-slide images, align them with pathology language, retrieve similar cases, and generate report-like text.

That sounds very big because it is very big.

A whole-slide image is not like a normal photograph. It is a gigapixel object. It can contain tissue architecture, tumor regions, stroma, necrosis, inflammation, artifacts, empty background, scanner effects, staining differences, and clinically meaningful patterns at multiple scales. For years, much of computational pathology has worked by chopping slides into small patches, encoding those patches, and then using another model to pool or aggregate the information. TITAN tries to make the slide itself the object of representation.

The clean version is:

- TITAN is a Vision Transformer operating on grids of patch embeddings from whole-slide images.
- It is pretrained on 335,645 whole-slide images from Mass General Brigham and GTEx.
- It uses three stages: vision-only self-supervised learning, ROI-caption alignment using synthetic captions, and whole-slide/report alignment using pathology reports.
- It performs strongly on slide-level classification, molecular prediction, survival prediction, few-shot learning, zero-shot classification, rare cancer retrieval, cross-modal retrieval, and report generation.
- Its most interesting clinical promise is not just prediction. It is retrieval and decision support: finding similar slides and reports for difficult cases.
- Its most interesting weakness is trust infrastructure: provenance, audit logs, report lineage, black-box reduction, and governance around synthetic text and clinical deployment.

This note is therefore both a paper summary and an argument about what should sit around models like TITAN. The technical question is: can we build methods around whole-slide foundation models that make them more auditable, more clinically accountable, and less opaque?

## Why this paper exists

The introduction starts from a problem in computational pathology: patch-level foundation models have become powerful, but clinical questions are often slide-level or patient-level.

A patch encoder can learn useful histology features from millions of small regions of tissue. It can represent cellular morphology, local architecture, and stain patterns. But a diagnosis or prognosis often depends on how those local regions relate to the whole specimen. A pathologist does not only look at one square crop. They move across the slide, compare regions, notice where tumor is dense, where stroma appears, where necrosis begins, and where tissue context changes the meaning of local morphology.

The paper argues that current patch-based systems leave a gap between feature extraction and clinical use. The gap appears in several places.

First, a whole-slide image is enormous. A model cannot simply treat it as a normal image.

Second, patient cohorts are often small, especially for rare diseases. A supervised task-specific model may not have enough examples.

Third, useful pathology data are not only visual. Reports contain diagnostic language, tissue site information, microscopic findings, and clinical context, although they are noisy and not always perfectly aligned to a single slide.

Fourth, pathology AI needs more than classification. Clinicians may want to retrieve similar cases, compare reports, or ask whether a rare tumor resembles archived examples.

TITAN is proposed as a general-purpose slide representation model that tries to handle all of this at once. It takes patch features, keeps their spatial arrangement, learns a slide embedding, and aligns that embedding with pathology text.

The paper positions this as a move from "patch foundation model plus downstream aggregator" toward an off-the-shelf whole-slide foundation model.

## The model in one sentence

TITAN is a transformer-based slide encoder that represents a whole-slide image as a spatial grid of patch embeddings and learns that representation through vision-only self-supervision plus vision-language alignment with synthetic ROI captions and real pathology reports.

That sentence hides several important design choices.

The model does not ingest raw gigapixel pixels directly. Instead, the authors divide each slide into 512 x 512 pixel patches at 20x magnification. Each patch is passed through CONCHv1.5, a pathology patch encoder. TITAN then works in the embedding space of those patch features. In other words, CONCHv1.5 acts like the patch embedding layer of a normal Vision Transformer.

The slide is represented as a two-dimensional feature grid. This matters because pathology is spatial. If the model treated patches as an unordered bag, it could lose tissue architecture. By keeping the grid, the model can use positional information and attention.

The difficult trick is that training on full slides would be computationally expensive. TITAN trains on 8,192 x 8,192 pixel regions, represented as 16 x 16 feature grids, then applies the model to larger slide contexts at inference. The authors use ALiBi positional bias, extended to two dimensions, to help the transformer generalize from shorter training contexts to longer slide-level contexts.

The paper calls the vision-only model TITANV. After language alignment, the full multimodal model is called TITAN.

## Section summary: Introduction

The introduction is doing three jobs.

First, it explains why foundation models matter in pathology. Self-supervised patch encoders have already shown that pathology images contain reusable visual patterns. Once a model learns histological features, those features can be used for diagnosis, prognosis, biomarker prediction, and downstream clinical endpoints.

Second, it argues that patch-level progress is not enough. Whole-slide images contain long-range context and patient-level meaning. Current approaches often require additional specialized models to aggregate patch embeddings, which makes clinical translation harder. The paper presents whole-slide foundation models as a way to simplify this: encode the whole slide once, then use the embedding for many tasks.

Third, it identifies limitations in prior slide models. Some are vision-only and cannot use pathology reports. Some use fewer pretraining samples than patch foundation models. Some require end-to-end training or fine-tuning. Some are not evaluated deeply enough in clinically important low-data settings such as rare cancer retrieval.

The authors' thesis is that a slide model should learn from both morphology and language, and should be evaluated on tasks that look closer to real pathology workflows: few-shot diagnosis, zero-shot language-guided classification, report generation, and retrieval of similar cases.

The introduction immediately raises a governance question. If slide embeddings become a reusable clinical substrate, then the embedding itself becomes an object that needs provenance. We should know which slide generated it, which patch encoder produced the tokens, which model version created the embedding, what preprocessing occurred, and what clinical report text was used for alignment.

## Section summary: Scaling SSL from patches to whole-slide images

The first Results section explains how TITAN is trained.

The pretraining dataset, Mass-340K, contains 335,645 whole-slide images and 182,862 reports. It spans 20 organs, multiple stains, different tissue types, and several scanner types. The dataset is heavily neoplastic but includes normal, inflammatory, tissue damage response, and other categories. Most slides are H&E, with smaller proportions of IHC and special stains.

The training has three stages.

Stage 1 is vision-only self-supervised learning. The model learns slide-level morphology from patch feature grids using iBOT, a self-supervised approach based on masked image modeling and student-teacher distillation. This stage creates TITANV.

Stage 2 aligns image regions with generated text. The authors use PathChat to create 423,122 synthetic captions for 8,192 x 8,192 pixel regions. These captions describe morphology at a finer level than ordinary clinical reports usually do.

Stage 3 aligns whole slides with pathology reports. The model is trained on 182,862 whole-slide/report pairs. This gives the slide embedding a connection to clinical language and enables zero-shot classification, report generation, and cross-modal retrieval.

The technical heart of this section is how the model handles slide scale. Whole slides can contain more than 10,000 patch tokens. Training directly on that scale is expensive, so TITAN learns from sampled regions. Each 8k region becomes a 16 x 16 grid of patch features. From each region, the training process creates global and local crops for self-supervised learning.

The positional encoding choice is important. The authors use a two-dimensional version of ALiBi, where attention is biased according to distance between patches in the grid. This helps the transformer preserve spatial context and makes it more plausible to train on smaller regions and infer on larger slides.

This section is one of the strongest parts of the paper because it is a practical engineering answer to a real pathology problem. It does not pretend that gigapixel slides can be handled like ordinary images. It builds a representation pipeline around the constraints.

My main concern is that several important transformations happen before the final embedding exists: tissue segmentation, tiling, patch encoding, feature augmentation, grid construction, region sampling, positional bias, and multimodal alignment. Each step is a potential source of error or bias. A clinical-grade system would need to log each step, not just the final model output.

## Section summary: Diagnostic and slide-level capabilities

The next Results section evaluates whether TITAN's slide embeddings are useful.

The authors compare TITAN and TITANV against existing slide foundation models including PRISM, GigaPath, and CHIEF, as well as mean pooling and supervised baselines such as attention-based multiple instance learning.

The evaluation covers many task types:

- morphological classification
- cancer subtyping
- grading
- molecular classification
- immunohistochemistry-related prediction
- survival prediction
- noncancerous transplant rejection tasks

The paper also introduces two evaluation resources based on TCGA. TCGA-UniformTumor-8K is a region-level pan-cancer task with 25,495 tumor-containing 8k regions across 32 classes. TCGA-OncoTree is a whole-slide pan-cancer classification task with 11,186 slides across 46 OncoTree classes.

The main result is that TITAN and TITANV generally outperform the other slide encoders. The paper reports especially strong performance on morphological subtyping, including difficult pan-cancer classification and noncancerous tasks. TITAN also performs well for molecular prediction and survival analysis, although mean pooling remains competitive for survival, suggesting that simple proportions of morphology may still carry strong prognostic information.

A useful detail is the comparison between model size and performance. TITAN is smaller than some baseline slide encoders but performs strongly, which supports the claim that pretraining design and spatial context matter, not only parameter count.

The paper also examines embedding structure. TITAN embeddings cluster by organ and tumor type while mixing submission sites more effectively, which the authors interpret as better biological organization and less site-driven clustering. They also show attention heatmaps where different attention heads focus on dense tumor, tumor-adjacent stroma, or non-tumor regions.

The attention heatmaps are useful, but they are not a complete explanation. They tell us where attention may concentrate, not whether the model's reasoning is clinically correct. This is a black-box reduction opportunity. An improved method could pair attention with concept-level evidence, retrieved neighbor cases, morphology summaries, stain/scanner metadata, and uncertainty traces.

## Section summary: Different learning paradigms

This section asks whether pretrained slide embeddings are actually better than simpler or more supervised approaches.

The comparison includes mean pooling, ABMIL, linear probing on frozen embeddings, and fine-tuning from either random or pretrained weights.

The pattern is important:

- ABMIL beats mean pooling, which makes sense because ABMIL learns task-specific attention.
- TITAN linear probing beats ABMIL, suggesting that the pretrained slide embedding already captures useful morphology and context.
- Fine-tuning TITAN can improve performance further when enough training data exist.
- Fine-tuning from random initialization performs worse, which supports the value of pretraining.

This is a strong practical message. TITAN is not only a model for huge labs with large labeled cohorts. It is useful as a frozen representation, as a few-shot substrate, and as an initialization for fine-tuning.

This suggests a possible governance layer around model use modes. A clinical AI system should record whether a prediction came from:

- a frozen foundation embedding plus linear probe
- a few-shot prototype classifier
- a task-specific fine-tuned model
- a retrieval workflow
- a zero-shot text prompt workflow

Those modes have different risk profiles. A zero-shot prompt result should not be governed like a validated supervised classifier. Fine-tuned models should carry training cohort details. Retrieval systems should preserve the identities and metadata of returned comparison cases.

## Section summary: Few-shot learning

The few-shot section is one of the most clinically interesting parts of the paper.

Rare diseases are a recurring challenge in medical AI. If a cancer type has few examples, a conventional supervised model may not be viable. TITAN is evaluated with only a small number of labeled examples per class, including one-shot, two-shot, four-shot, eight-shot, and sixteen-shot settings.

The reported pattern is that TITAN performs best across tasks and shot counts. TITANV is usually second best, which suggests that the vision-only representation already captures much of the needed morphology, while language alignment adds further value.

The most striking claim is that TITAN can be much stronger than ABMIL in very low-data settings, especially on rare pan-cancer tasks. This makes sense if the foundation model has already learned broad morphological structure from pretraining. A small labeled set can then anchor the classes without training a large model from scratch.

This is where the model connects most clearly to clinical reality. Rare cancers are exactly where expertise, examples, and diagnostic confidence may be scarce. A retrieval or few-shot system could help pathologists compare a difficult case to similar archived cases.

But this also raises safety questions. Few-shot performance can be fragile. The choice of the few examples matters. A mislabeled support case could distort the prototype. A site-biased support set could make the model retrieve institution-specific artifacts rather than disease morphology.

A useful extension would be support-set governance:

- record who selected each support example
- store the diagnostic basis for the label
- track whether labels were confirmed by molecular testing, expert consensus, or report text
- warn when support examples come from only one institution, scanner, or staining protocol
- maintain audit logs when support sets are changed

That is not glamorous model architecture work, but it is exactly the kind of infrastructure that makes clinical AI safer.

## Section summary: Language-aligned TITAN

This section evaluates what language alignment adds.

TITAN is tested on zero-shot classification, where diagnostic labels are converted into text prompts and embedded by the text encoder. A slide is classified by finding the closest text embedding to the slide embedding.

The paper compares TITAN with PRISM, another multimodal pathology model. TITAN performs much better in zero-shot classification across multiple tasks, especially multiclass tasks. The authors argue that the combination of fine-grained ROI captions and slide-level reports matters. ROI captions teach local morphology language. Reports teach diagnostic and slide-level language.

This is conceptually elegant. Pathology language exists at different scales. A report may say "invasive ductal carcinoma" or "glioblastoma, WHO grade IV", but a morphological description might mention necrosis, mitotic activity, gland formation, stromal reaction, or cellular atypia. TITAN uses synthetic captions to fill the gap between local visual features and high-level report diagnoses.

The paper also evaluates report generation using TCGA-Slide-Reports, a dataset of 10,108 slide-report pairs. TITAN beats PRISM on METEOR, ROUGE, and BLEU. The examples suggest that TITAN can generate reports that capture tissue site, diagnosis, grade, and representative morphology better than PRISM in selected cases.

This is exciting and dangerous at the same time.

Report generation is not the same as diagnosis. A generated report can sound fluent while being wrong, incomplete, or overly confident. Metrics such as ROUGE and BLEU measure text overlap, not clinical safety. METEOR is somewhat richer but still not a substitute for expert validation.

This is a rich area for improvement. A safer report-generation system might not generate a polished final report. It could instead generate structured draft observations with evidence links:

- tissue site hypothesis
- possible diagnosis
- key morphology found
- morphology not found
- regions supporting each claim
- nearest similar slides and their confirmed diagnoses
- uncertainty and differential diagnoses
- missing data or low-confidence areas
- model version, prompt version, and preprocessing hash

That would shift the system from black-box text generation toward auditable clinical support.

## Section summary: Rare cancer and cross-modal retrieval

The retrieval section may be the most persuasive clinical use case.

Instead of asking the model to output a diagnosis directly, retrieval asks it to find similar slides or reports. This fits pathology practice more naturally. When facing a rare or difficult case, clinicians often benefit from comparison to previous cases, atlases, reports, and expert examples.

The paper creates several rare cancer retrieval datasets. Rare-Cancer combines rare and common cancer types across TCGA, EBRAINS, and internal MGB data. Rare-Cancer-Public uses public data only. Rare-Cancer-External tests generalization on 39 slides from Kanagawa Cancer Center Hospital in Japan, covering rare ovarian and soft tissue cancers.

The model retrieves candidate slides from a database and is evaluated by whether the top K results include the same diagnostic label as the query. TITAN performs best overall and is especially strong on the external rare cancer set, where domain shift matters.

The paper also evaluates cross-modal retrieval on TCGA-Slide-Reports. This means two directions:

- given a report, retrieve relevant slides
- given a slide, retrieve relevant reports

TITAN outperforms PRISM in both directions.

For clinical deployment, retrieval may be more defensible than autonomous generation. It can preserve human judgment: the model does not have to decide; it can surface comparison cases. But retrieval still needs governance. A retrieved case can mislead if its label is wrong, its report is outdated, its institution uses different terminology, or its tissue preparation differs substantially.

An improved retrieval system should show provenance beside every retrieved case:

- source institution or dataset
- scan date and scanner
- stain and tissue preparation
- diagnosis label and label authority
- report availability
- known molecular or IHC confirmation
- similarity score and embedding model version
- reason codes or concept-level similarity, where possible
- whether the case was part of pretraining

That last point matters. If a model retrieves cases it saw during pretraining or evaluation, clinicians and researchers should know. It changes how we interpret performance and trust.

## Section summary: Discussion

The discussion presents TITAN as a general-purpose whole-slide foundation model with immediate potential for pathology workflows.

The authors emphasize several contributions:

- scaling successful patch-level self-supervised learning recipes to slide-level representation learning
- using a Vision Transformer with two-dimensional ALiBi for long-context slide inference
- combining vision-only pretraining with language alignment at both ROI and whole-slide scales
- showing strong performance across classification, prognosis, few-shot, zero-shot, retrieval, and report-generation tasks
- demonstrating that retrieval may help with rare cancers and diagnostically difficult cases

The limitations are important.

First, training on 8k regions and extrapolating to full slides may still miss some whole-slide context. ALiBi helps, but it does not prove that every clinically relevant global pattern is captured.

Second, slide models can encode nonbiological signals. Scanner type, staining protocol, tissue processing, and institution-specific artifacts can leak into embeddings. The paper does include robustness analyses around submission site clustering, but this remains a serious translational issue.

Third, pathology report processing is difficult. Reports are noisy, often patient-level rather than slide-level, and may include details unrelated to morphology. Aligning slides to reports requires automated cleaning and mapping. This is a possible source of hidden label noise.

Fourth, the pretraining dataset is large but still smaller than some patch-level pretraining datasets. The authors expect scaling data and architecture to improve performance.

The discussion ends with an optimistic view: models like TITAN could become part of routine pathology toolkits, used alongside task-specific supervised systems.

My reading is cautiously enthusiastic. TITAN is impressive, and the clinical direction makes sense. But the closer such systems get to clinical support, the more the missing infrastructure matters. A high-performing foundation model is not yet a clinical system. It needs data lineage, model lineage, uncertainty communication, human override, failure analysis, monitoring, and institutional governance.

## Section summary: Methods

The Methods section gives the details needed to understand how much engineering sits underneath the headline results.

The ethics statement says the internal retrospective data and reports were approved by the Mass General Brigham Institutional Review Board. Internal digital data were anonymized, and informed consent was waived because the work used archival pathology slides without direct patient recruitment.

The pretraining dataset combines internal MGB slides, consult slides, and GTEx. It includes scanner and stainer diversity. The authors note 16 scanners from seven manufacturers, more than 100 IHC stains, and more than 50 special stains.

For synthetic caption generation, PathChat creates detailed morphology descriptions for 8k ROIs. Because PathChat cannot directly process full 8k regions, each ROI is split into 64 smaller 1,024 x 1,024 patches. K-means clustering selects representative patches, and PathChat describes them. Qwen2-7B-Instruct rewrites captions to diversify language.

For slide-report data, the authors process clinical reports to extract slide-specific descriptions and remove sensitive or irrelevant information. Qwen2-7B-Instruct is used locally for cleaning and rewriting. This is a major part of the pipeline because real pathology reports are not automatically machine-learning-ready.

For visual preprocessing, the authors use CLAM for tissue segmentation and tiling. Slides are segmented using the saturation channel in HSV space, cleaned with median blurring and morphological operations, and tiled into 512 x 512 patches at 20x magnification. CONCHv1.5 extracts a 768-dimensional feature for each patch.

For visual pretraining, TITANV uses iBOT on 16 x 16 feature grids. The model sees two global crops and ten local crops per sampled region. This is the slide-level analogue of self-supervised learning on image crops.

For multimodal pretraining, the authors use CoCa. The architecture includes an image encoder, text encoder, and multimodal decoder. Stage 2 uses ROI-caption pairs with a large effective batch size. Stage 3 uses whole-slide/report pairs and crops slides to 64 x 64 feature grids, covering a much larger field of view.

The slide encoder itself is compact: six transformer layers, 12 attention heads, embedding dimension 768, and hidden dimension 3,072. TITANV is trained on four A100 80GB GPUs, while multimodal TITAN uses eight A100 80GB GPUs. Downstream experiments are run on a single 24GB RTX 3090.

The evaluation methods are broad. The paper uses linear probing, k-nearest neighbor probing, slide retrieval, cross-modal retrieval, few-shot classification, survival analysis, zero-shot classification, and report generation. Metrics include balanced accuracy, weighted F1, AUROC, quadratic-weighted Cohen's kappa, concordance index, expected calibration error, entropy, Accuracy@K, majority-vote Accuracy@5, Recall@K, METEOR, ROUGE, and BLEU.

The authors also use hierarchical generalized linear mixed-effects models for statistical comparisons across datasets.

This Methods section is a reminder that "foundation model" does not mean simple model. It means a large socio-technical pipeline of image handling, metadata handling, text cleaning, model training, evaluation design, and statistical testing.

## Questions the paper leaves open

The paper leaves four groups of questions.

First, data and provenance:

- Which slides were internal, consult, or public?
- Which slides were part of pretraining versus evaluation?
- How much scanner, stainer, and site metadata is retained in downstream use?
- Can every embedding be traced back to a slide, preprocessing recipe, patch encoder, and TITAN version?

Second, report alignment:

- How often do cleaned reports still contain slide-irrelevant information?
- How often is a patient-level report incorrectly mapped to a slide?
- How much does the model learn from diagnostic terminology rather than morphology?
- Are generated captions ever wrong in ways that become amplified by pretraining?

Third, interpretability:

- Are attention heatmaps stable across perturbations?
- Can retrieved cases explain the model better than attention maps alone?
- Can the model produce concept-level morphology evidence?
- Can it say what evidence is missing?

Fourth, clinical governance:

- Should report generation be used at all, or should the system produce structured evidence instead?
- How should uncertainty be shown to pathologists?
- What audit logs are required for a clinical retrieval session?
- How should a hospital monitor model drift across scanners, stains, and departments?

## Research direction: an audit layer for whole-slide foundation models

The most natural next step is not to retrain TITAN from scratch. That would be expensive and probably unnecessary.

A more realistic and useful direction would be an audit and provenance layer around whole-slide foundation model workflows.

The aim would be to define and implement a lightweight framework for tracking how a whole-slide AI output was produced.

At minimum, the system would record:

- slide identifier
- source dataset or institution
- scanner and stain metadata
- tissue segmentation settings
- tile size and magnification
- patch encoder name and version
- slide encoder name and version
- preprocessing code version
- embedding hash
- prompt template, if using zero-shot classification
- support set identity, if using few-shot learning
- retrieval database version, if using slide search
- generated text model and decoding settings, if using report generation
- user identity and timestamp for each model query
- returned outputs and uncertainty values

This would let a user reconstruct why an output existed. It would also help answer whether a changed output came from a model update, preprocessing change, prompt change, retrieval database change, or support-set change.

That is the kind of infrastructure medical AI needs before it becomes trustworthy at scale.

## Research direction: provenance-aware retrieval

Retrieval is clinically promising, so a focused method could build a prototype retrieval interface that does not only show "similar cases".

It would show similar cases with provenance cards.

Each card could include:

- diagnosis and diagnostic authority
- tissue site
- stain
- scanner
- institution or dataset
- report excerpt or structured diagnosis
- similarity score
- whether the case was used in model pretraining
- whether molecular confirmation exists
- model explanation signals

The research question would be whether provenance-aware retrieval changes trust calibration. Do users become less likely to overtrust retrieved cases when scanner, site, and label provenance are visible? Do they notice when all similar cases come from one institution? Do they use uncertainty more appropriately?

This could become a human factors and governance study rather than only a machine learning benchmark.

## Research direction: black-box reduction through evidence bundles

TITAN includes attention heatmaps, but attention alone is not enough.

An evidence bundle could combine:

- top attended regions
- nearest retrieved slides
- nearest retrieved reports
- morphology concepts extracted from generated captions
- uncertainty and calibration metrics
- data provenance
- prompt or support-set details

Instead of saying "the model predicts X", the system would say:

"The model places this slide near these confirmed examples, attends to these regions, associates them with these morphology concepts, and has this level of uncertainty. The result was produced by this model version on this date using this preprocessing pipeline."

That would not make the model fully interpretable, but it would make the output less opaque and more contestable.

Contestability is a good word for medical AI. A clinician should be able to challenge the output, inspect its basis, and decide whether it deserves weight.

## Research direction: synthetic caption governance

TITAN's use of synthetic captions is clever. It gives the model fine-grained morphology language at a scale that would be hard to obtain manually.

But synthetic captions introduce a new lineage problem. If a generative model creates the training text, then the generated text should itself be treated as data with provenance.

A synthetic caption governance framework could record:

- source ROI
- ROI sampling method
- captioning model
- prompt
- generation settings
- rewrite model
- rewrite prompt
- quality-control status
- reviewer notes, if any
- whether the caption was used for training

It could also flag risks:

- hallucinated morphology
- overly generic descriptions
- missing negations
- diagnostic leakage
- inconsistent terminology
- captions that overfit to common tumor patterns

The broader research question is whether synthetic clinical language improves representation learning while also creating hidden bias. That is exactly the kind of question I would like to explore.

## Research direction: model cards for slide embeddings

A whole-slide embedding should have a model card.

Not only the model itself, but the embedding artifact.

For example:

- what slide produced this embedding?
- what tissue regions were included or excluded?
- what patches were background-masked?
- what magnification and patch size were used?
- what patch encoder generated the features?
- what slide encoder generated the embedding?
- what training data distribution shaped the encoder?
- what known weaknesses apply?
- what clinical tasks is the embedding validated for?
- what tasks should it not be used for?

This could be implemented as a simple JSON schema first. Later it could connect to W3C PROV, model cards, datasheets for datasets, or healthcare audit standards.

## What I think the paper does very well

The paper is strong because it joins several ideas that belong together.

It treats whole-slide pathology as a multiscale problem. It does not reduce the slide to isolated patches or pretend that one magnification level is enough.

It uses language in a pathology-specific way. Reports and morphology captions are not just extra metadata; they are part of the representation learning strategy.

It evaluates low-data and rare disease settings. This is important because many medical AI papers look best where data are abundant, while clinical need is often sharpest where data are scarce.

It makes retrieval central. Retrieval feels more clinically grounded than standalone classification because it supports comparison, second opinion, and human reasoning.

It includes a serious range of baselines and tasks. The paper is not just one benchmark with one headline metric.

## What I would be careful about

I would be careful about clinical overclaiming. Strong benchmark performance does not mean the model is ready to write reports in a live diagnostic workflow.

I would be careful about text generation. A generated report can look reassuring even when it contains an error. In clinical settings, fluency is a risk factor as well as a feature.

I would be careful about synthetic captions. They may improve alignment, but they also import the assumptions and mistakes of the captioning model.

I would be careful about hidden site effects. The paper addresses this, but scanner, stain, institution, and tissue processing artifacts remain a central problem in computational pathology.

I would be careful about data access and reproducibility. Some data are internal and can only be shared under institutional conditions. That is understandable for privacy, but it affects independent replication.

I would be careful about evaluation metrics for report generation. BLEU, ROUGE, and METEOR are useful but not enough for clinical meaning.

## Where this leaves me

This paper sits where several important medical AI questions meet:

- imaging models that do not hide uncertainty
- clinical context that survives across workflow stages
- foundation models that support, rather than replace, expert reasoning
- provenance and auditability as first-class design goals
- governance for high-risk AI systems
- black-box reduction through evidence, retrieval, and traceability

The path I see is not "build a better TITAN" immediately. It is:

- understand TITAN and related models deeply
- reproduce a small retrieval or embedding workflow if feasible
- design a provenance schema for slide AI outputs
- prototype an audit log around model inference
- build an evidence-bundle format for retrieved cases, attention regions, prompts, and uncertainty
- evaluate whether this improves transparency and reduces overtrust

That is a research path with a real identity. It sits between machine learning, medical imaging, clinical workflow, and AI governance.

## References

- Ding, T. et al. (2025). [A multimodal whole-slide foundation model for pathology](https://doi.org/10.1038/s41591-025-03982-3). Nature Medicine.
- Mahmood Lab. [TITAN code and model loading repository](https://github.com/mahmoodlab/TITAN).
- Chen, R. J. et al. (2024). [Towards a general-purpose foundation model for computational pathology](https://www.nature.com/articles/s41591-024-02857-3). Nature Medicine.
- Xu, H. et al. (2024). [A whole-slide foundation model for digital pathology from real-world data](https://www.nature.com/articles/s41586-024-07441-w). Nature.

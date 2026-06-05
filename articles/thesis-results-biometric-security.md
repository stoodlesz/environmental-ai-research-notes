---
title: "What my thesis found about adversarial attacks on biometric authentication"
date: 2026-06-05
summary: "A plain-language summary of my MSc thesis results on adversarial attacks, facial embeddings, authentication thresholds, and lightweight defensive controls."
slug: thesis-results-biometric-security
---

# What my thesis found about adversarial attacks on biometric authentication

My MSc dissertation explored adversarial attacks on AI-based biometric authentication systems, focusing on facial recognition systems that use embedding-based verification.

The central idea was simple: in biometric authentication, the important question is not only whether a model misclassifies an image. The security question is whether an attacker can move a face representation close enough to another identity that the system accepts it.

That means the key metric is authentication boundary crossing.

In this project, I evaluated attacks using cosine similarity thresholds, rather than treating the task as a normal image classification problem. This mattered because biometric systems often work by comparing two embeddings and granting access if the similarity score exceeds a predefined threshold.

## Research questions

The thesis focused on four questions:

- How vulnerable are embedding-based facial authentication systems to targeted adversarial attacks?
- Do lightweight defences meaningfully reduce authentication compromise?
- How do pixel-space and latent-space attacks differ in impact and feasibility?
- How can biometric authentication be more securely deployed in resource-constrained environments?

## Experimental setup

The experiments used a pretrained FaceNet-style embedding model, with LFW and CASIA-WebFace used as facial datasets. The authentication decision was based on cosine similarity, with fixed thresholds around 0.80 and 0.85.

I tested two main attack routes:

- pixel-space adversarial attacks, including targeted PGD
- latent-space optimisation using StyleGAN2-ADA

The experiments were deliberately constrained. They were run in a CPU-only environment, which made runtime and feasibility part of the research question rather than just an inconvenience.

## Result 1: pixel-space attacks shifted embeddings, but rarely caused impersonation

Pixel-space attacks increased similarity between the source and target identities, but they rarely crossed the authentication threshold.

The baseline source-to-target cosine similarity was usually around 0.20 to 0.40. After adversarial optimisation, the adversarial-to-target cosine similarity rose to roughly 0.55 to 0.75.

That is a meaningful movement in embedding space. The attack was doing something real.

But with an authentication threshold of 0.80, false acceptance remained rare.

This suggests that pixel-space attacks can distort embeddings and push identities closer together, but under the tested constraints they were not usually enough to produce a full biometric impersonation.

## Result 2: full latent inversion was powerful, but expensive

The full latent-space attack used inversion plus targeted optimisation. This was much more effective.

In the inversion-based latent attack, the final cosine similarity reached 0.9809 and crossed the authentication threshold. That is similarity comparable to a genuine identity match.

The cost was compute time:

- inversion runtime: 35 hours
- optimisation runtime: 43 hours
- total runtime: around 78 hours
- final cosine similarity: 0.9809
- threshold crossed: yes

This result is important because it shows that identity-level convergence is possible, but it also shows that the most powerful version of the attack was not cheap or fast.

## Result 3: the reduced-compute latent variant was the most interesting security result

The reduced-compute latent variant removed the reconstruction stage and used direct latent optimisation.

This made the attack much more feasible while still producing authentication-relevant similarity.

Across five runs, the reduced-compute variant achieved:

- success rate: 100 percent
- mean cosine similarity: 0.8626
- mean runtime: 105.97 minutes
- non-target cosine similarity: -0.1121

This was the most interesting result from a security perspective.

The full pipeline reached higher similarity, but it took around 78 hours. The reduced-compute variant reached a mean cosine above the tested authentication threshold in under two hours on average.

That makes the risk feel more operationally realistic.

## Result 4: attack capability was graded, not binary

One of the main conclusions was that adversarial capability should not be treated as a yes-or-no property.

The results formed a graded capability pattern:

- pixel-space attacks were fast and repeatable, but usually stayed below the authentication threshold
- reduced-compute latent optimisation was slower, but crossed the threshold more realistically
- the full latent pipeline achieved the strongest identity convergence, but with low repeatability and high computational cost

So the security question becomes more nuanced:

Not "can this system be attacked?"

But "what level of compute, access, and optimisation is required to cross the authentication boundary?"

## Defensive controls

I also tested lightweight defensive controls that could be applied around the authentication system without retraining the embedding model.

The secure wrapper included:

- rate limiting
- similarity logging
- monotonic similarity increase detection
- account lockout
- a step-up authentication band

The value of these controls is that they target suspicious authentication behaviour rather than trying to make the embedding model perfect.

This is important for small and medium-sized organisations, where retraining or replacing a biometric model may not be realistic.

## What this means

The thesis conclusion was that authentication compromise depends on boundary crossing, not ordinary model misclassification.

Pixel-space attacks can distort embeddings, but in my tests they rarely induced impersonation. Latent-space attacks were more dangerous because they could create identity-level convergence. Reduced-compute latent optimisation was especially important because it showed that meaningful attack feasibility may exist even under constrained resources.

The defensive conclusion was also practical: operational controls can reduce attack feasibility without modifying the underlying model.

This matters because biometric systems process sensitive identity data. Under GDPR, biometric data receives special protection. Under the EU AI Act, biometric and high-risk AI systems raise additional questions around risk management, robustness, and accountability.

For me, the biggest lesson was that biometric AI security has to be evaluated as an authentication problem, not just a machine learning benchmark.

## References

- European Parliament and Council (2016). [Regulation (EU) 2016/679, General Data Protection Regulation](https://eur-lex.europa.eu/eli/reg/2016/679/oj).
- European Parliament and Council (2024). [Regulation (EU) 2024/1689, Artificial Intelligence Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj).
- Goodfellow, I. J., Shlens, J. and Szegedy, C. (2015). [Explaining and Harnessing Adversarial Examples](https://arxiv.org/abs/1412.6572).
- Kilany, S. and Mahfouz, A. (2025). [A comprehensive survey of deep face verification systems adversarial attacks and defense strategies](https://pubmed.ncbi.nlm.nih.gov/40847113/).
- Madry, A., Makelov, A., Schmidt, L., Tsipras, D. and Vladu, A. (2018). [Towards Deep Learning Models Resistant to Adversarial Attacks](https://openreview.net/forum?id=rJzIBfZAb).
- Schroff, F., Kalenichenko, D. and Philbin, J. (2015). [FaceNet: A Unified Embedding for Face Recognition and Clustering](https://openaccess.thecvf.com/content_cvpr_2015/html/Schroff_FaceNet_A_Unified_2015_CVPR_paper.html).
- Yang, J., Liu, Z., Hu, Z., Yu, T. and Loy, C. C. (2020). Adversarial robustness of deep face recognition: A closer look. ECCV 2020.
- Williams, S. (2025). [Adversarial Attacks on AI-Based Biometric Authentication Systems](https://github.com/stoodlesz/final-clean-msc-biometric-security).

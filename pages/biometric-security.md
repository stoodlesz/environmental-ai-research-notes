---
title: "Biometric Security"
summary: "Adversarial attacks on AI-based biometric authentication systems, based on my MSc dissertation project."
slug: biometric-security
---

# Biometric Security

This project is based on my MSc dissertation work: adversarial attacks on AI-based biometric authentication systems.

The research investigates adversarial manipulation in facial biometric authentication systems that use embedding-based facial recognition. Instead of focusing only on classification error, the project looks at authentication-relevant outcomes: cosine similarity, threshold behaviour, false acceptance risk, and whether attacks could move an identity representation close enough to compromise a biometric system.

The work connects AI security, adversarial machine learning, biometric authentication, and practical defensive thinking.

## Project focus

- evaluate adversarial vulnerabilities in facial recognition systems
- test pixel-space attacks such as FGSM and PGD
- explore latent-space impersonation using StyleGAN2-ADA
- analyse authentication thresholds using cosine similarity
- focus on false acceptance and identity convergence rather than only classification error
- evaluate lightweight mitigation strategies suitable for small and medium-sized organisations
- work under constrained compute conditions, including CPU-only experimentation

## Why it matters

Biometric systems are often treated as secure because they are tied to identity, but AI-based biometric authentication can still be vulnerable to manipulation. A system can appear accurate in a normal benchmark while still behaving dangerously under adversarial pressure.

This project is about asking security-focused questions: what would compromise look like, how close does an embedding need to get, what signals could detect suspicious behaviour, and how can defensive controls be made practical rather than theoretical.

## Ethical focus

The attack work is framed as defensive research. The goal is to understand vulnerabilities so that biometric systems can be evaluated more realistically and protected more carefully.

This also connects back to the wider theme of the site: AI systems should be tested not just for performance, but for robustness, misuse potential, explainability, and real-world risk.

## Repository

The project repository is available here:

[stoodlesz/final-clean-msc-biometric-security](https://github.com/stoodlesz/final-clean-msc-biometric-security)

=> [See all projects](project.html)

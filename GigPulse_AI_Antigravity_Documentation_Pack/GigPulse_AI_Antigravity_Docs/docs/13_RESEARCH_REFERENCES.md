# Research and Technical References

**Use:** Starting bibliography for the project. Re-check publication metadata, versions, licences and current policy before citing in a final academic submission. The references below are leads, not a substitute for reading the full paper/document and following your institution's citation style.

## Gig and platform work context

1. NITI Aayog. (2022). *India’s Booming Gig and Platform Economy: Perspectives and Recommendations on the Future of Work*. June 2022. Official report PDF: https://niti.gov.in/sites/default/files/2023-02/25th_June_Final_Report_27062022.pdf . Use for India-specific background and definitions as stated in the report; do not reuse historical projections as current statistics without checking the report's year and methodology.

## Spatio-temporal demand forecasting

2. “A Sageformer-KAN deep learning model for demand prediction of online food deliveries.” *Expert Systems with Applications* (online publication reported March 25, 2026). ScienceDirect record: https://www.sciencedirect.com/ (search exact paper title). Review its data, prediction unit, baselines and evaluation before using it as evidence for this project's design.

3. Bhat, R. L., & Gillani, I. A. (2025). “Spatio-Temporal Demand Prediction for Food Delivery Using Attention-Driven Graph Neural Networks.” arXiv:2507.15246. https://arxiv.org/abs/2507.15246 . Treat the arXiv version as a preprint; verify any claimed journal publication and DOI independently before citing a journal version.

## Geospatial systems and maps

4. H3: Uber’s Hexagonal Hierarchical Spatial Index. Official documentation: https://h3geo.org/docs/ . The official documentation describes H3 as a hierarchical hexagonal geospatial index and states that the H3 project is Apache 2.0 licensed. Review resolution choice and privacy implications before implementation.

5. OpenStreetMap Foundation. Copyright and licence: https://www.openstreetmap.org/copyright . OpenStreetMap data is licensed under ODbL; attribution is required and share-alike obligations may apply when adapting the database. Review the specific use and separate data licensing from tile-service terms.

## Weather data (optional adapter)

6. Open-Meteo API documentation: https://open-meteo.com/en/docs ; current terms and data licence summary: https://github.com/open-meteo/open-meteo . The provider describes free API access for open-source/non-commercial use, requires contact for commercial use, and offers data under CC BY 4.0 with attribution. Re-check the live terms and use context before integration; cache responses and preserve observation/forecast issue timestamps.

## Indian data protection context

7. Government of India. *Digital Personal Data Protection Act, 2023* (Act No. 22 of 2023). Official Gazette PDF hosted by MeitY: https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf .

8. Government of India. *Digital Personal Data Protection (DPDP) Rules, 2025*, notified 14 November 2025. Press Information Bureau backgrounder: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2190655&lang=1&reg=3 ; MeitY Rules page: https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025 . Also inspect commencement notification G.S.R. 843(E), 13 November 2025: https://egazette.gov.in/WriteReadData/2025/267647.pdf and any subsequent official amendments/notifications. Different provisions may commence on different dates; determine the provisions actually in force at the time of deployment. This project document is not legal advice.

## Methodology references to add during literature review

9. Forecast evaluation: find authoritative literature on rolling-origin evaluation, temporal leakage, intermittent demand and probabilistic forecast calibration.
10. Earnings modelling: add peer-reviewed research on gig-work earnings, worker-level heterogeneity, platform incentives and net-income estimation.
11. Responsible AI: consult NIST AI Risk Management Framework and relevant worker-platform governance research; map controls to the actual use case.

## Source hygiene

For every final reference, record DOI or stable URL, publication date, accessed date, peer-review/preprint status, target variable, geographical setting, data scale, method, baseline and limitations. Cite the primary paper rather than blogs summarizing it.

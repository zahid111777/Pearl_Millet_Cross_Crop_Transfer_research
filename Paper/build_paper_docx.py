"""Build the manuscript (.docx) from the recorded results.

Every number in the tables is read from Paper/tables/*.md, which build_tables.py
generates from the experiment CSVs. Prose numbers were checked against the same files.

Run:  PYTHONPATH=<dir with python-docx> python Paper/build_paper_docx.py [--endnote]
      --endnote writes EndNote temporary citations ({Author, Year}) and no typed reference list;
      open that file in Word and run EndNote > Update Citations and Bibliography.
"""
import json
import sys
from pathlib import Path
from docx_builder import Manuscript, read_md_table

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TAB = HERE / "tables"
FIG_P = HERE / "figures"
FIG_C = ROOT / "Experiments" / "figures"
FIG_V = ROOT / "Experiments_vit_b16" / "figures"
ENDNOTE = "--endnote" in sys.argv
OUT = HERE / ("Pearl_Millet_Cross_Crop_Transfer_Manuscript_EndNote.docx" if ENDNOTE
              else "Pearl_Millet_Cross_Crop_Transfer_Manuscript.docx")

refs = json.load(open(HERE / "references_verified.json", encoding="utf-8"))
m = Manuscript(refs, endnote=ENDNOTE)


def verdict(v):
    return v.split(" (")[0]


def short_ci(s):
    return s.replace(" ", "")


# =========================================================== title block
m.p("**Does intermediate rice-disease pre-training help data-poor pearl-millet disease "
    "classification? A specimen-grouped evaluation with ConvNeXt and Vision Transformer models**",
    align="center", size=15, after=10)
m.p("Zahid Rashid^1,*^ and Shawal Nasir^1^", align="center", size=11.5, after=2)
m.p("^1^ CareCloud, {{HL:[city, country — authors to confirm]}}", align="center", size=10, after=2)
m.p("Zahid Rashid, AI Engineer, zahidrasheed0123@gmail.com", align="center", size=10, after=0)
m.p("Shawal Nasir, Junior AI Engineer, shawalnasir353@gmail.com", align="center", size=10, after=2)
m.p("^*^ Corresponding author: Zahid Rashid (zahidrasheed0123@gmail.com)", align="center", size=10, after=14)

# =========================================================== abstract
m.h("Abstract", 1)
m.p("Pearl millet is a staple cereal of the semi-arid tropics, yet labelled images of its diseases are scarce. "
    "The usual answer to scarce data is to fine-tune a network pre-trained on ImageNet, and a popular refinement "
    "is to add an intermediate training stage on a large dataset from a related crop. We tested whether such a "
    "stage, using the Paddy Doctor rice-disease dataset (10,274 images after auditing), improves the classification "
    "of five pearl-millet classes (228 images after de-duplication) beyond ImageNet pre-training alone. We compared "
    "ImageNet, ImageNet→rice and random→rice initialisation for ConvNeXt-Tiny and ViT-B/16 at 10, 25, 50 and 100 % of "
    "the target training data, keeping folds, training subsets, seeds and the training recipe identical across "
    "conditions (1,620 pearl-millet training runs in total). While auditing the data we found that repeated "
    "photographs of the same leaf were spread across the original cross-validation folds: 42 % of test images had a "
    "near-identical specimen in the training folds. We therefore built specimen-grouped folds, which lowered "
    "macro-F1 by 0.06–0.09. Under this protocol, rice pre-training gave no measurable gain over ImageNet at any data "
    "fraction. Paired macro-F1 differences ranged from −0.011 to +0.008 for ConvNeXt-Tiny and from −0.031 to −0.016 "
    "for ViT-B/16, and every fold-level 95 % confidence interval included zero. Rice pre-training without ImageNet "
    "was far better than random initialisation (+0.27 to +0.31 macro-F1) but remained below ImageNet. Most of the "
    "remaining error came from *Exserohilum rostratum*, a class with nine images, three of which were photographed "
    "against the same background as the *Pyricularia* images and were almost always classified as *Pyricularia*. "
    "The models were under-confident, which we traced to label smoothing and class-weighted loss. For small "
    "plant-disease collections, we conclude that ImageNet fine-tuning is a strong baseline, and that "
    "specimen-level evaluation with honest uncertainty reporting is needed before any claim about the value of "
    "related-crop pre-training.")
m.p("**Keywords:** pearl millet; plant disease classification; transfer learning; intermediate pre-training; "
    "rice; ConvNeXt; Vision Transformer; data leakage; specimen-grouped cross-validation; calibration",
    align="left", after=12)

# =========================================================== 1 introduction
m.h("1. Introduction", 1)
m.h("1.1 Background", 2)
m.p("Pearl millet (*Pennisetum glaucum* (L.) R. Br.) is widely grown in the arid and semi-arid "
    "regions of sub-Saharan Africa and South Asia, often on poor soils and under rainfall that would defeat most "
    "other cereals [@jukanti2016]. It is an important source of food and nutrition for smallholder households, and its "
    "tolerance of drought, heat and marginal soils makes it increasingly relevant as the climate warms. Like any crop, "
    "it suffers from diseases. Blast, caused by *Pyricularia grisea* (teleomorph *Magnaporthe grisea*), has become a "
    "serious disease of forage and grain pearl millet in India [@sharma2013]. Downy mildew, caused by *Sclerospora "
    "graminicola*, is regarded as its most important disease and can cause almost total grain loss in susceptible "
    "crops [@singh1993;thakur2008]. Smut and *Exserohilum* leaf blight are among the other fungal diseases recorded on "
    "the crop [@usda_pm]. In practice, these diseases are identified by eye, by extension workers or by the farmers "
    "themselves, and accurate diagnosis depends on expertise that is not always available in the field.", indent=True)
m.p("Deep convolutional networks can recognise plant diseases from photographs with high accuracy when large "
    "labelled collections are available [@mohanty2016;ferentinos2018;kamilaris2018]. The difficulty is that such "
    "collections exist for only a handful of crops. Rice, wheat, maize and tomato have public datasets with thousands "
    "of images, whereas pearl millet, despite its importance for food security, has very few. The public pearl-millet "
    "collection used in this study contains 281 raw images in five classes, of which 228 remain after duplicates are "
    "removed, and one class has only nine images [@pm_dataset]. At this scale, training a network from scratch is not "
    "a realistic option.", indent=True)
m.p("The standard way to cope with little data is transfer learning. A network is first trained on a large "
    "general-purpose corpus, most often ImageNet [@deng2009;russakovsky2015], and then fine-tuned on the small target "
    "task [@yosinski2014;kornblith2019]. A natural extension is to insert an intermediate stage: after ImageNet, the "
    "network is trained on a large dataset from a related domain before it sees the target data. In natural-language "
    "processing, continued pre-training on in-domain data has been shown to help [@gururangan2020;pruksachatkun2020], "
    "and in plant pathology it seems intuitive that features learned from the lesions of one cereal should carry over "
    "to another. Rice is an attractive source for pearl millet. The Paddy Doctor collection provides more than ten "
    "thousand labelled rice-disease images [@paddydoctor_paper;paddydoctor_kaggle], and some rice and pearl-millet "
    "diseases are caused by related pathogens, blast being the clearest example.", indent=True)

m.h("1.2 Problem statement", 2)
m.p("Whether an intermediate rice stage actually helps *beyond* ImageNet initialisation, and whether it helps more "
    "when the target data are scarcest, has rarely been tested under controlled conditions. A fair test needs every "
    "initialisation to be trained and evaluated on exactly the same images with the same recipe, and it needs the "
    "uncertainty of the comparison to be reported. With a few hundred target images, differences of a few points of "
    "macro-F1 can easily arise from the choice of folds or random seeds alone.", indent=True)
m.p("A second problem concerns evaluation itself. Small plant-image collections are often built by photographing "
    "the same leaf or plant several times, for example with slightly different framing. When such repeats end up in "
    "both the training and the test partitions, the score partly measures recognition of a specimen the model has "
    "already seen rather than generalisation to new plants [@kapoor2023;barz2020]. Exact-hash and perceptual-hash "
    "de-duplication catch identical or almost identical files, but they miss repeats that differ in framing. Leakage "
    "of this kind inflates absolute accuracy and can also distort comparisons between methods. Related problems, "
    "such as models exploiting background or acquisition conditions rather than symptoms, have been documented for "
    "the widely used PlantVillage dataset [@noyan2022;geirhos2020].", indent=True)

m.h("1.3 Research questions and contributions", 2)
m.p("This paper addresses four research questions about cross-crop transfer for data-poor pearl-millet disease "
    "classification:", indent=True)
m.bullets([
    "**RQ1.** Does intermediate pre-training on rice improve classification over ImageNet pre-training alone, and "
    "is any benefit larger when only 10 %, 25 % or 50 % of the target training data are available?",
    "**RQ2.** Does knowledge from rice help when ImageNet is not used, that is, rice-only pre-training compared with "
    "random initialisation?",
    "**RQ3.** Do the answers depend on the architecture, comparing a convolutional network (ConvNeXt-Tiny) with a "
    "vision transformer (ViT-B/16)?",
    "**RQ4.** How much does the evaluation protocol matter when repeated photographs of the same specimen are kept "
    "out of the training folds?",
])
m.p("Our contributions are as follows. First, we report a controlled comparison of ImageNet, ImageNet→rice and "
    "random→rice initialisation, plus a random-initialisation lower bound for ConvNeXt, at four target-data fractions. "
    "Every condition and both architectures share the same folds, training subsets, seeds, training recipe and "
    "metrics. Second, we present a leakage analysis of the pearl-millet collection and a specimen-grouped evaluation "
    "protocol. In the original folds, 42 % of test images had a near-identical same-class specimen in the training "
    "folds, while the grouped folds have none, and grouping lowered macro-F1 by 0.06–0.09. Third, we use "
    "uncertainty-aware statistics: fold-level paired differences with effect sizes and intervals, an image-level "
    "bootstrap, multiplicity correction and a conservative decision rule fixed in advance. Fourth, we provide "
    "diagnostic studies of the weakest class and of calibration, carried out without using the test folds for any "
    "selection.", indent=True)
m.p("The rest of the paper is organised as follows. Section 2 reviews related work. Section 3 describes the "
    "datasets, the evaluation protocol, the models and the statistical analysis. Section 4 gives the experimental "
    "setup. Section 5 reports the results, Section 6 discusses them, Section 7 sets out the limitations, and "
    "Section 8 concludes.", indent=True)

# =========================================================== 2 literature review
m.h("2. Literature review", 1)
m.h("2.1 Deep learning for plant disease recognition", 2)
m.p("Mohanty et al. [@mohanty2016] trained AlexNet and GoogLeNet on the PlantVillage collection of about 54,000 "
    "leaf images [@hughes2015] and reported 99.35 % accuracy on a held-out set from the same collection. On images "
    "taken under different conditions, however, accuracy fell to 31.4 %. Ferentinos [@ferentinos2018] trained "
    "networks on a larger open database of 87,848 images covering 25 plants and 58 plant–disease classes and reached "
    "a best success rate of 99.53 %. Kamilaris and Prenafeta-Boldú [@kamilaris2018] surveyed 40 deep-learning studies "
    "in agriculture and found that deep learning generally gave high accuracy and outperformed conventional "
    "image-processing techniques. Barbedo [@barbedo2018] examined 12 plant species and 56 diseases and found that "
    "transfer-learning accuracy ranged from 60 % to 100 % depending on the crop, with the size and variety of the "
    "training data as key factors. Too et al. [@too2019] compared fine-tuned architectures on 38 PlantVillage classes "
    "and found DenseNet-121 the most accurate (99.75 %) while using fewer parameters. Together, these studies show "
    "that very high accuracies are achievable on large, uniform "
    "collections, but they say less about the small, heterogeneous datasets that are typical of neglected crops.", indent=True)
m.h("2.2 Rice and pearl-millet disease datasets and models", 2)
m.p("Rice is one of the best-served crops in terms of public image data. Lu et al. [@lu2017] trained a CNN on about "
    "500 field images of ten rice diseases, and Rahman et al. [@rahman2020] fine-tuned VGG16 and InceptionV3 on field "
    "images with heterogeneous backgrounds and proposed a two-stage small CNN that reached 93.3 % accuracy. The "
    "Paddy Doctor dataset [@paddydoctor_paper] contains 16,225 smartphone images of paddy leaves in 13 classes, taken "
    "in real fields in Tamil Nadu and labelled with an agronomist. Its authors reported a best F1 of 97.50 % with "
    "ResNet34. A 10,407-image, ten-class subset was released as a Kaggle competition [@paddydoctor_kaggle], and that "
    "subset is our source domain.", indent=True)
m.p("Pearl millet is much less studied. Coulibaly et al. [@coulibaly2019] used ImageNet transfer learning with "
    "feature extraction to identify mildew in pearl-millet images and reported 95.00 % accuracy. Kundu et al. "
    "[@kundu2021] combined IoT data collection with a deep-learning detector and feature visualisation for pearl-millet "
    "blast and rust. Johnson et al. [@johnson2024] trained a custom CNN on about 3,400 field images of five diseases "
    "and healthy leaves and reported 98.86 % accuracy, ahead of several standard architectures. Ramya et al. "
    "[@ramya2026] segmented rust, blast and downy-mildew lesions with an attention-based Mask R-CNN and noted that the "
    "small number of diseased images risks overfitting and dataset bias. These works report high accuracies on their "
    "own data, but none asks whether knowledge from a better-resourced crop can substitute for scarce pearl-millet "
    "images, and none examines whether repeated photographs of the same plant affect the reported scores. The "
    "pearl-millet dataset used here [@pm_dataset] is openly licensed, which makes it possible to study these "
    "questions reproducibly.", indent=True)
m.h("2.3 Transfer learning and intermediate pre-training", 2)
m.p("Yosinski et al. [@yosinski2014] showed that features in the early layers of a convolutional network are "
    "general, while those in later layers become specific to the training task, and that transferring features, "
    "even from a distant task, is better than random initialisation. Kornblith et al. [@kornblith2019] found that "
    "ImageNet accuracy correlates strongly with transfer accuracy across 12 target datasets, but that ImageNet "
    "pre-training helped little on two small fine-grained datasets. He et al. [@he2019] showed that object detectors "
    "trained from random initialisation on COCO can match ImageNet-pre-trained ones, with pre-training mainly "
    "speeding up convergence. Raghu et al. [@raghu2019] found that, on two large medical-imaging tasks, ImageNet "
    "pre-training gave little performance benefit, small models matched large ones, and part of the transfer effect "
    "came from the scaling of the pre-trained weights rather than from feature reuse. Neyshabur et al. "
    "[@neyshabur2020] found that part of the benefit of transfer comes from low-level statistics of the data, and "
    "that models fine-tuned from the same pre-trained weights stay close to one another in parameter space.", indent=True)
m.p("Intermediate pre-training adds a stage between the generic corpus and the target task. In natural-language "
    "processing, Gururangan et al. [@gururangan2020] showed that continued pre-training on in-domain text improves "
    "downstream performance in both high- and low-resource settings. Pruksachatkun et al. [@pruksachatkun2020] tested "
    "110 intermediate–target pairs and found that the gains depended on the pairing, with intermediate tasks that "
    "require high-level inference helping most. In plant pathology, Singh et al. [@singh2020] reported that "
    "fine-tuning on their field-image PlantDoc dataset after PlantVillage pre-training raised field-image accuracy by "
    "up to 31 % over ImageNet-only transfer. Xu et al. [@xu2022] pre-trained a ViT on the plant-domain PlantCLEF2022 "
    "dataset, starting from ImageNet weights, and transferred it to 12 plant-disease datasets in few-shot settings. "
    "Al Sahili and Awad [@alsahili2022] released agriculture-pre-trained versions of five ImageNet architectures "
    "trained on about 160,000 images. These studies make in-domain pre-training plausible. To our knowledge, however, "
    "none has tested a single related-crop disease dataset as an intermediate stage for a target crop with only a few "
    "hundred images, compared it with ImageNet under matched conditions at several data fractions, and reported "
    "paired uncertainty under specimen-level evaluation.", indent=True)
m.h("2.4 Convolutional networks and vision transformers", 2)
m.p("We used two families of architecture. ConvNeXt [@liu2022] modernises the ResNet design with larger kernels, "
    "fewer activation and normalisation layers, and training choices borrowed from transformers. It reaches 87.8 % "
    "ImageNet top-1 accuracy and outperforms Swin Transformers on COCO detection and ADE20K segmentation. The Vision "
    "Transformer (ViT) "
    "[@dosovitskiy2021] splits an image into fixed-size patches and processes them with a standard transformer "
    "encoder. ViT performs best when pre-trained on very large datasets and is known to need more data than "
    "convolutional networks, because it lacks their built-in locality bias. DeiT [@touvron2021] showed that ViTs can "
    "be trained competitively on ImageNet-1k alone with strong augmentation and distillation. Comparing the two "
    "families on the same small target task lets us ask whether the value of rice pre-training depends on the "
    "inductive bias of the network.", indent=True)
m.h("2.5 Data leakage, near-duplicates and grouped evaluation", 2)
m.p("Kapoor and Narayanan [@kapoor2023] reviewed machine-learning-based science and found data leakage affecting "
    "294 papers in 17 fields, sometimes leading to wildly overoptimistic conclusions. In computer vision, Barz and "
    "Denzler [@barz2020] found near-duplicates of 3.3 % of the CIFAR-10 test images and 10 % of the CIFAR-100 test "
    "images in the training sets, and accuracy dropped when these were replaced. Noyan [@noyan2022] showed that a "
    "classifier given only eight background pixels from each PlantVillage image, with no leaf information, reached "
    "49.0 % accuracy against a chance level of 2.6 %. That dataset therefore contains background cues correlated with "
    "the labels. Geirhos et al. [@geirhos2020] describe such shortcuts as a general failure mode of deep networks: the "
    "model learns a decision rule that works on the benchmark but fails under real-world distribution shift. "
    "Perceptual hashing [@zauner2010] is the usual tool for finding near-identical images by comparing compact hashes "
    "with the Hamming distance. It is designed for copies and re-encodings of the same photograph, not for a "
    "specimen that has been photographed again. When observations "
    "share a source, such as the same plant or site, Roberts et al. [@roberts2017] recommend blocked or grouped "
    "cross-validation so that dependent samples never fall on both sides of a split. We follow that advice by "
    "grouping images of the same specimen.", indent=True)
m.h("2.6 Calibration, class imbalance and statistical comparison", 2)
m.p("A classifier used for decision support should produce probabilities that match its accuracy. Guo et al. "
    "[@guo2017] showed that modern deep networks are often poorly calibrated and that a single temperature parameter "
    "fitted on held-out data is a simple and effective remedy. The expected calibration error (ECE) [@naeini2015] and "
    "the Brier score [@brier1950] are standard measures. Label smoothing [@szegedy2016] is widely used as a "
    "regulariser, and Müller et al. [@muller2019] showed that it improves generalisation and calibration and pulls "
    "same-class representations into tight clusters. Class imbalance is known to hurt convolutional networks "
    "[@buda2018;johnson2019]. Cui et al. [@cui2019] proposed weighting the loss by the inverse of the effective number "
    "of samples per class. We use this weighting, and we show later that, combined with label smoothing, it explains "
    "the under-confidence of our models.", indent=True)
m.p("Comparing classifiers on small datasets requires care. Dietterich [@dietterich1998] showed that common tests on "
    "resampled data have inflated type-I error, and Nadeau and Bengio [@nadeau2003] explained why: cross-validation "
    "folds share training data, so the per-fold results are not independent and their variance is underestimated. "
    "Bouckaert and Frank [@bouckaert2004] added that a test's outcome can depend strongly on the particular random "
    "partition of the data. Demšar [@demsar2006] recommended non-parametric tests and caution with multiple "
    "comparisons. We therefore treat the fold, not the run, as the "
    "unit of inference. We report paired effect sizes [@lakens2013], exact permutation tests [@phipson2010], an "
    "image-level bootstrap [@efron1993] and Holm correction [@holm1979], and we use macro-F1 and balanced accuracy "
    "[@brodersen2010] because they are less affected by class imbalance than plain accuracy.", indent=True)
m.h("2.7 Research gap", 2)
m.p("Previous work shows that ImageNet transfer is effective for plant disease recognition. It also shows that "
    "intermediate in-domain pre-training can help in some settings, and that evaluation on small or "
    "single-source datasets can be overoptimistic. What is missing is a controlled test of related-crop "
    "intermediate pre-training for a genuinely data-poor crop that (i) compares it with ImageNet under identical "
    "conditions, (ii) examines the low-data regime where it should matter most, (iii) checks more than one "
    "architecture, and (iv) uses an evaluation protocol that keeps repeated photographs of the same specimen apart. "
    "This study is designed to fill that gap for pearl millet.", indent=True)

# =========================================================== 3 methods
m.h("3. Materials and methods", 1)
m.p("Figure 1 summarises the full pipeline. It has two data streams, rice as the source and pearl millet as the "
    "target, two training stages, and a common evaluation and analysis layer. Each block is described in the "
    "subsections below.", indent=True)
m.fig(FIG_P / "fig1_methodology.png",
      "Overview of the study design. The rice data are audited and used only for pre-training (Stage 1). The "
      "pearl-millet data are cleaned, grouped by specimen and split into five folds, which, together with the data "
      "fractions and seeds, define the experiments in Stage 2. Each pearl-millet network starts from one of four "
      "initialisations and is fine-tuned with a fixed recipe. All runs are scored with the same metrics and compared "
      "with paired statistics.")
m.p("The pipeline proceeds in six steps. (1) Both datasets are audited for exact and near-duplicate images, and "
    "conflicting rice labels are removed. (2) Pearl-millet images are grouped into inferred specimens, and five "
    "folds are built so that no specimen is split. (3) For each architecture, a rice model is trained from ImageNet "
    "weights and another from random weights, and the best checkpoint on rice validation data is kept. (4) Each "
    "pearl-millet network is initialised with ImageNet weights, a rice checkpoint or random weights, given a new "
    "five-class head, and fine-tuned for a fixed number of epochs on the training folds of one (fold, seed, fraction) "
    "combination. (5) Predictions on the held-out fold are stored. (6) Metrics are computed and compared across "
    "initialisations with paired tests at the fold level.", indent=True)

m.h("3.1 Datasets", 2)
m.h("3.1.1 Target dataset: pearl millet", 3)
m.p("The target data come from a public pearl-millet disease image collection deposited on Zenodo "
    "[@pm_dataset]. It was collected in Burkina Faso and is released under a CC-BY-4.0 licence. The archive contains "
    "five class folders: *Pyricularia* sp. (blast), *Moesziomyces bullatus* (smut; the accepted name for the pathogen "
    "formerly called *M. penicillariae* [@li2019]), *Sclerospora graminicola* (downy mildew), *Exserohilum rostratum*, "
    "and healthy leaves, with 281 JPEG images in total. Image sizes vary "
    "widely: 174 of the 281 images are 4000×3000 pixels, and the rest range from about 460×1024 to 780×1040 pixels. "
    "The smut and downy-mildew images mostly show panicles, while the other classes show leaves (Fig. 2).", indent=True)
m.p("**Cleaning.** We removed 17 byte-identical files (MD5), leaving 264 images. Perceptual hashing (pHash, Hamming "
    "distance ≤ 4) then grouped 66 visually near-identical images into 30 groups. We kept one image per group and "
    "removed 36, leaving 228 images. Images were corrected for EXIF orientation and cached at no more than 512 pixels "
    "on the long side. The final class counts are given in Table 1.", indent=True)
m.fig(FIG_P / "fig2_samples.png",
      "Example images from the five pearl-millet classes after cleaning, with the number of images per class. "
      "Images are centre-cropped for display.")
m.h("3.1.2 Source dataset: rice (Paddy Doctor)", 3)
m.p("The source domain was the training set of the Paddy Doctor Kaggle competition [@paddydoctor_kaggle], a "
    "subset of the Paddy Doctor dataset [@paddydoctor_paper]: 10,407 images of 480×640 pixels in ten classes (bacterial leaf blight, bacterial leaf streak, bacterial panicle blight, blast, "
    "brown spot, dead heart, downy mildew, hispa, tungro and normal), with metadata on variety and plant age. All "
    "images decoded correctly. The audit found 72 exact-duplicate groups (74 redundant copies, none crossing class "
    "labels) and 27 near-duplicate pairs that carried different labels, which we confirmed visually as the same "
    "photograph labelled twice. We removed the 74 redundant copies, both images of each conflicting pair (39 "
    "images), and one image from each of 20 confirmed same-class near-duplicate pairs, leaving 10,274 images. The "
    "remaining pHash neighbours (distance ≤ 2) were kept but merged into 9,563 leakage groups that are never split. "
    "A grouped, class-stratified split gave 7,323 training, 1,483 validation and 1,468 test images. No rice image "
    "lies within pHash distance 6 of any pearl-millet image (minimum distance 12), so the rice data contain no "
    "target images.", indent=True)
m.table("Datasets after cleaning.",
        ["Dataset", "Role", "Classes", "Images", "Smallest / largest class", "Image size"],
        [["Pearl millet [@pm_dataset]", "Target", "5", "228 (of 281)", "9 (*E. rostratum*) / 98 (*Pyricularia*)",
          "460×1024 to 4000×3000"],
         ["Paddy Doctor (Kaggle) [@paddydoctor_kaggle]", "Source (pre-training only)", "10", "10,274 (of 10,407)",
          "337 / 1,764 (raw)", "480×640"]],
        widths_cm=[3.4, 3.0, 1.6, 2.6, 3.6, 2.6],
        note="Pearl-millet class counts: *Pyricularia* 98, smut 75, *S. graminicola* 23, healthy 23, *E. rostratum* 9.")

m.h("3.2 Evaluation protocol and specimen grouping", 2)
m.p("Pearl-millet performance was estimated with five-fold cross-validation. We report two fold assignments. The "
    "first, called the original or v1 protocol, used StratifiedGroupKFold [@pedregosa2011] with the pHash ≤ 4 "
    "clusters as groups. Inspecting the v1 folds showed that the collection contains several photographs of the same "
    "leaf with different framing, often with consecutive file numbers. These pairs had pHash distances of 6–35, too "
    "large for hashing to catch, but ImageNet-feature cosine similarities of 0.95–0.99, and they were spread across "
    "different folds.", indent=True)
m.p("To quantify this, we computed for each test image its highest cosine similarity to any same-class image in "
    "the training folds. Features were the global-average-pooled, L2-normalised outputs of an ImageNet-pre-trained "
    "ConvNeXt-Tiny at 288 pixels. Because these features contain no rice information, they favour neither "
    "pre-training arm. We then built the second, specimen-grouped protocol, which is the primary protocol in this "
    "paper. Within each class, images were clustered by average linkage at a cosine threshold of 0.93, giving 124 "
    "specimen groups (largest 16 images), and StratifiedGroupKFold(5) was applied to these groups. Among 300 "
    "candidate shuffles, we chose the one with no empty class–fold cell and the most balanced fold sizes (shuffle "
    "seed 140). **This choice used labels and group membership only, never model results.** Fold sizes are "
    "48/42/44/45/49 images, and the nine *Exserohilum* images fall 1/1/1/1/5 across the folds. Both fold manifests "
    "were written once and never regenerated, and the ViT experiments check that their splits are identical to those "
    "used for ConvNeXt.", indent=True)
m.p("**Data fractions.** To study the low-data regime, each training set was sub-sampled to 10 %, 25 % or 50 % "
    "within each class (rounded, at least two images per class), with the random state set to the seed. The test "
    "fold was always complete. For a given fold, seed and fraction, every model and both architectures therefore "
    "train on exactly the same images. The mean training-set sizes were 20, 46, 91 and about 182 images at 10, 25, "
    "50 and 100 %. *Exserohilum* contributed two training images at 10 % and 25 %, two to four at 50 %, and four to "
    "eight at 100 %, depending on the fold.", indent=True)

m.h("3.3 Models and initialisation", 2)
m.p("Both architectures share one interface: a backbone, dropout of 0.3 and a linear classification head. "
    "**ConvNeXt-Tiny** [@liu2022] has 27.8 M parameters and uses the torchvision IMAGENET1K_V1 weights, with "
    "stochastic depth [@huang2016] rising from 0 to 0.1. **ViT-B/16** [@dosovitskiy2021] has 85.8 M parameters, uses "
    "the torchvision [@torchvision2016] IMAGENET1K_V1 weights and reads out from the class token. Its 14×14 position-embedding grid "
    "was bicubically resampled to 20×20 for the 320-pixel input. We had planned a size-matched DeiT-Small "
    "[@touvron2021], but its pre-trained weights could not be downloaded in our environment, so the two architectures "
    "differ in capacity as well as in design.", indent=True)
m.p("Every pearl-millet network received a new five-class head and started from one of these initialisations:", indent=True)
m.bullets([
    "**ImageNet**: ImageNet-1k weights, fine-tuned directly on pearl millet.",
    "**ImageNet → rice**: ImageNet weights, then supervised training on rice (Stage 1), then pearl millet.",
    "**random → rice**: random weights, then supervised training on rice, then pearl millet. This isolates what rice "
    "alone contributes, without ImageNet.",
    "**random**: random weights trained directly on pearl millet (ConvNeXt only), as a lower bound.",
])

m.h("3.4 Stage 1: rice pre-training", 2)
m.p("Rice models were trained with full fine-tuning and a ten-class head on the rice training split. We used AdamW "
    "[@loshchilov2019] (β = 0.9/0.999, weight decay 0.05) with a peak learning rate of 4×10^−4^, layer-wise "
    "learning-rate decay of 0.8 [@clark2020;bao2022], 10 % linear warm-up followed by cosine decay [@loshchilov2017], gradient "
    "clipping at 1.0, batch size 64, 320-pixel inputs and bf16 mixed precision. The loss was cross-entropy with label "
    "smoothing 0.1 [@szegedy2016] and effective-number class weights (β = 0.999) [@cui2019]. With layer-wise decay, "
    "layer *l* of *L* receives the learning rate", indent=True)
m.eq("η~l~ = η · γ^L−l^,   γ = 0.8,")
m.p("and the class weight for class *c* with *n*~c~ training images is", align="left")
m.eq("w~c~ ∝ (1 − β) / (1 − β^n~c~^),   β = 0.999.")
m.p("The checkpoint with the best validation macro-F1 was kept, with an early-stopping patience of 4 epochs. "
    "ImageNet → rice used 15 epochs. Random → rice used up to 100 epochs with patience 10, because a 15-epoch "
    "random-initialised model was clearly under-trained (validation macro-F1 0.36 and still rising). That model is "
    "kept on record but was not used. For ViT we declared in advance that the ImageNet → rice job would be stopped if "
    "the loss became non-finite or validation macro-F1 was below 0.30 after epoch 3. The run passed this check, with "
    "0.89 at epoch 3. Rice checkpoints were trained once, never overwritten, and never chosen on the basis of "
    "pearl-millet results.", indent=True)

m.h("3.5 Stage 2: transfer to pearl millet", 2)
m.p("The rice head was discarded and a new head trained. For ConvNeXt we compared three transfer policies: a "
    "**linear probe** (head only), **partial fine-tuning** (last down-sampling layer, last stage and final norm) and "
    "**full fine-tuning** (layer-wise decay 0.8, head learning rate ×10). ViT was run with full fine-tuning only, "
    "with its layer-wise decay rescaled so that the lowest layer receives the same relative learning rate as the "
    "ConvNeXt stem (0.8^7^ ≈ 0.21). Pearl-millet training used the same optimiser, loss and augmentation as Stage 1, "
    "with a peak learning rate of 2×10^−4^ (×5 for the linear probe), **40 epochs, no validation set and no "
    "checkpoint selection**. With 228 images and a nine-image class there is no room for an inner validation set, "
    "and choosing the epoch on the test fold would leak information. No hyper-parameter was tuned on pearl-millet "
    "data, and the same settings were used for every initialisation, fraction and architecture. Because the number "
    "of epochs is fixed, runs with fewer images take fewer optimiser steps. A sensitivity check with 80 epochs is "
    "reported in Section 5.9.", indent=True)
m.p("**Augmentation.** Training images were randomly resized and cropped to 320×320 pixels (scale 0.4–1, aspect "
    "ratio 3/4–4/3), flipped horizontally and vertically, rotated by up to ±20° with probability 0.5, given mild "
    "colour jitter, and normalised with ImageNet statistics. At evaluation, images were resized directly to 320×320.", indent=True)

m.h("3.6 Evaluation metrics", 2)
m.p("The primary metric is macro-F1, the unweighted mean of the per-class F1 scores. For class *c* with precision "
    "*P*~c~ and recall *R*~c~,", indent=True)
m.eq("F1~c~ = 2 *P*~c~ *R*~c~ / (*P*~c~ + *R*~c~),   macro-F1 = (1/*C*) Σ~c~ F1~c~,")
m.p("and balanced accuracy is the mean per-class recall, (1/*C*) Σ~c~ *R*~c~. Because a class can be missing from a "
    "test fold, fold-level macro-F1 is averaged over the classes present in that fold. We also report accuracy and "
    "per-class F1, pooled over the five out-of-fold test sets and averaged over seeds. Calibration was measured with "
    "the expected calibration error over *B* = 15 equal-width confidence bins,", align="left")
m.eq("ECE = Σ~b~ (|*B*~b~| / *n*) · | acc(*B*~b~) − conf(*B*~b~) |,")
m.p("together with the negative log-likelihood and the Brier score. Per-fold ECE uses only about 45 images, so it is "
    "noisy and biased upward. Where logits were saved, we prefer ECE pooled over all 228 out-of-fold predictions. "
    "Temperature scaling [@guo2017] divides the logits *z* by a scalar *T* > 0 fitted on held-out data, giving "
    "softmax(*z*/*T*). In our calibration study, *T* was fitted on a calibration fold that was disjoint from the "
    "test fold.", align="left")

m.h("3.7 Statistical analysis", 2)
m.p("Folds share training data and seeds share folds, so the 15 runs per condition (5 folds × 3 seeds) are not "
    "independent [@nadeau2003]. We therefore used the fold as the unit of inference: seeds were averaged within "
    "each fold, giving five paired values per comparison. For the paired differences Δ~1~, …, Δ~5~ we report the "
    "mean difference, Cohen's *d*~z~ [@lakens2013], a 95 % *t* interval with 4 degrees of freedom, and the number of "
    "folds in which the first model wins:", indent=True)
m.eq("*d*~z~ = mean(Δ) / sd(Δ),   95 % CI = mean(Δ) ± *t*~0.975, 4~ · sd(Δ) / √5.")
m.p("We also ran an exact sign-flip permutation test over the five folds [@phipson2010]. Its smallest attainable "
    "two-sided *p*-value is 0.0625, so it can never reach 0.05, and we report it only for completeness. As a "
    "complementary analysis, we computed an image-level paired bootstrap [@efron1993] of the difference in pooled "
    "out-of-fold macro-F1 (4,000 resamples, stratified by class, with identical resamples for both models). This "
    "captures test-set sampling uncertainty but ignores fold-to-fold training variability, so it is optimistic on "
    "its own. *P*-values were Holm-corrected [@holm1979] within pre-defined families of comparisons.", indent=True)
m.p("**Decision rule.** A difference was called *supported* only if the Holm-adjusted bootstrap *p* was below 0.05, "
    "the bootstrap 95 % interval excluded zero, and the sign agreed in at least four of the five folds. Otherwise it "
    "was called *inconclusive*, never \"no effect\". The rule was fixed before the ViT and data-fraction experiments "
    "were run. All other comparisons are exploratory.", indent=True)

# =========================================================== 4 experimental setup
m.h("4. Experimental setup", 1)
m.h("4.1 Hardware and software", 2)
m.p("All experiments ran on a workstation with two NVIDIA GeForce RTX 5090 GPUs (32 GB each), an Intel Core "
    "i9-14900K CPU and 128 GB of RAM, under Linux. The GPUs were shared with other workloads, so jobs were limited "
    "to the memory that was free; this prevented a planned 448-pixel variant, which we replaced with 384 pixels in "
    "an exploratory study. The software stack was Python 3.12.3, PyTorch 2.14.0 with CUDA 13.0 [@paszke2019], "
    "torchvision 0.29.0, scikit-learn 1.7.2 [@pedregosa2011], NumPy 2.3.5, pandas 2.3.3, SciPy 1.16.3, Pillow 12.2 "
    "and ImageHash 4.3.2. One epoch of rice pre-training for ConvNeXt-Tiny took about 9 seconds, and the full "
    "15-epoch ImageNet → rice run took about 2.5 minutes.", indent=True)
m.h("4.2 Training configuration", 2)
m.p("Table 2 lists the training configuration. The same values were used for both architectures and for every "
    "initialisation, fraction and seed. Nothing was tuned on pearl-millet data.", indent=True)
m.table("Training configuration.",
        ["Setting", "Stage 1 (rice)", "Stage 2 (pearl millet)"],
        [["Optimiser", "AdamW, β = (0.9, 0.999), weight decay 0.05", "same"],
         ["Peak learning rate", "4×10^−4^", "2×10^−4^ (linear probe ×5; head ×10)"],
         ["Layer-wise LR decay", "0.8", "0.8 (ViT rescaled to same lowest-layer ratio, 0.21)"],
         ["Schedule", "10 % linear warm-up, cosine decay", "same"],
         ["Epochs", "15 (ImageNet → rice); ≤ 100, patience 10 (random → rice)", "40, fixed"],
         ["Model selection", "best rice validation macro-F1 (patience 4)", "none (last epoch)"],
         ["Batch size / input", "64 / 320×320 px", "64 / 320×320 px"],
         ["Loss", "CE, label smoothing 0.1, effective-number class weights (β = 0.999)", "same"],
         ["Regularisation", "dropout 0.3 before head; stochastic depth 0–0.1 (ConvNeXt)", "same"],
         ["Precision / clipping", "bf16 autocast / gradient norm 1.0", "same"],
         ["Augmentation", "random-resized crop (0.4–1), flips, rotation ±20°, colour jitter", "same"],
         ["Seeds", "fixed", "0, 1, 2 (training seed = 1000·seed + fold)"]],
        widths_cm=[3.6, 6.4, 6.4], font=8.5)
m.h("4.3 Experiment matrix", 2)
m.p("Table 3 lists all pearl-millet experiments. Each cell of the main grids is 5 folds × 3 seeds = 15 runs. In "
    "total we trained 1,620 pearl-millet models, plus five rice models (ConvNeXt: ImageNet → rice, random → rice and "
    "the unused 15-epoch random → rice; ViT: ImageNet → rice and random → rice).", indent=True)
m.table("Pearl-millet experiments. Runs are counted over folds, seeds and fractions.",
        ["Experiment", "Architecture", "Initialisations", "Policies", "Fractions", "Runs"],
        [["Main grid, specimen-grouped folds", "ConvNeXt-Tiny", "random, ImageNet, ImageNet→rice, random→rice",
          "linear, partial, full", "10/25/50/100 %", "480"],
         ["Main grid, original folds (v1)", "ConvNeXt-Tiny", "same", "same", "10/25/50/100 %", "480"],
         ["Architecture comparison", "ViT-B/16", "ImageNet, ImageNet→rice, random→rice", "full",
          "10/25/50/100 %", "180"],
         ["Calibration study", "ConvNeXt-Tiny", "ImageNet, ImageNet→rice", "full", "60 % (held-out cal. fold)", "150"],
         ["*Exserohilum* study", "ConvNeXt-Tiny", "ImageNet, ImageNet→rice", "full", "100 %", "150"],
         ["Steps-matched check (80 epochs)", "ConvNeXt-Tiny", "ImageNet, ImageNet→rice", "partial, full",
          "10/25/50 %", "180"],
         ["**Total**", "", "", "", "", "**1,620**"]],
        widths_cm=[4.0, 2.4, 4.0, 2.2, 2.4, 1.4], font=8.5)
m.h("4.4 Reproducibility safeguards", 2)
m.p("Runs were deterministic on our hardware: re-training a stored run reproduced its macro-F1 to within 10^−16^. "
    "Result files were append-only, and before each new batch of experiments we took a hashed snapshot of all earlier "
    "results, checkpoints and manifests and checked it again afterwards. The ViT code is a patched copy of the "
    "ConvNeXt code that writes only to its own directory. We confirmed that the shared code path was unchanged by "
    "re-running a stored ConvNeXt result through the ViT code, which reproduced it exactly. Expensive jobs could only "
    "be started through explicit flags, and existing checkpoints could not be overwritten.", indent=True)

# =========================================================== 5 results
m.h("5. Results", 1)
m.p("Unless stated otherwise, \"±\" denotes the standard deviation over the five folds, with seeds averaged within "
    "each fold, and all pearl-millet results use the specimen-grouped folds.", indent=True)

m.h("5.1 Rice pre-training", 2)
h, b = read_md_table(TAB / "T2.md")
m.p("Both architectures learned the rice task well (Table 4). ImageNet → rice reached a held-out macro-F1 of 0.968 "
    "for both ConvNeXt-Tiny and ViT-B/16. Random → rice reached 0.924 for ConvNeXt after 100 epochs and 0.940 for ViT, "
    "which stopped early at epoch 96. Models trained from random weights therefore learned useful rice features but "
    "stayed below the ImageNet-initialised ones. The rice test scores may be slightly optimistic, because rice "
    "near-duplicates at pHash distance 3–6 were not removed.", indent=True)
m.table("Held-out rice test performance (1,468 images).", h, b, widths_cm=[3.0, 4.0, 2.2, 2.6, 2.2, 2.0])

m.h("5.2 Repeated-specimen leakage in the original folds (RQ4)", 2)
h, b = read_md_table(TAB / "T1.md")
m.p("Many pearl-millet images are repeated photographs of the same leaf. Under the original folds, 96 of the 228 test "
    "images (42 %) had a near-identical same-class specimen (cosine ≥ 0.95) in the training folds, and the "
    "specimen-grouped folds removed all such cases (Fig. 3, Table 5). Moving from the original to the "
    "specimen-grouped folds lowered every macro-F1 estimate, by 0.056 to 0.094 for ConvNeXt at 100 % data (Table 6). "
    "Part of this change may come from the different fold composition, for example one fold holding five "
    "*Exserohilum* images, rather than from leakage alone. The grouped protocol also leaves moderately similar images "
    "across folds: 62 % of test images still have a same-class training image at cosine ≥ 0.90.", indent=True)
m.fig(FIG_P / "fig3_leakage.png",
      "Share of pearl-millet test images that have a same-class training image above a given ImageNet-feature cosine "
      "similarity, under the original and the specimen-grouped folds.", width_cm=12.5)
m.table("Test images (of 228) with a same-class training image above a cosine-similarity threshold.", h, b,
        widths_cm=[4.4, 5.0, 5.0])
h, b = read_md_table(TAB / "T8.md")
h[0] = "Initialisation"
m.table("Macro-F1 under the original and the specimen-grouped folds (ConvNeXt-Tiny, full fine-tuning, 100 % data).",
        h, b, widths_cm=[4.4, 3.6, 4.4, 3.0])

m.h("5.3 Effect of target-data fraction", 2)
m.p("Tables 7 and 8 and Fig. 4 give macro-F1 and balanced accuracy for the three main initialisations at each data "
    "fraction. Two patterns stand out. First, ImageNet-initialised ConvNeXt was almost insensitive to training-set "
    "size: macro-F1 was 0.801 ± 0.055 with about 20 training images and 0.807 ± 0.062 with the full set. ViT with "
    "ImageNet initialisation depended more on data, rising from 0.770 ± 0.053 at 10 % to 0.834 ± 0.078 at 100 %. "
    "Second, random → rice initialisation, without ImageNet, depended strongly on data for ConvNeXt (0.641 → 0.753) "
    "and less steadily for ViT (0.685 → 0.757). Fold-to-fold standard deviations (0.01–0.10) are as large as most "
    "differences between conditions, so the curves should be read together with their intervals. Accuracy for the "
    "same runs is given in Appendix Table A1.", indent=True)
h, b = read_md_table(TAB / "T3a.md")
m.table("Macro-F1 (mean ± SD over folds) by target-data fraction.", h, b,
        widths_cm=[2.8, 3.0, 2.65, 2.65, 2.65, 2.65])
h, b = read_md_table(TAB / "T3b.md")
m.table("Balanced accuracy (mean ± SD over folds) by target-data fraction.", h, b,
        widths_cm=[2.8, 3.0, 2.65, 2.65, 2.65, 2.65])
m.fig(FIG_V / "fractions_learning_curves.png",
      "Macro-F1 (top) and balanced accuracy (bottom) against the share of pearl-millet training data for ConvNeXt-Tiny "
      "(left) and ViT-B/16 (right). Lines are means of five fold-level values (seeds averaged), bands are 95 % "
      "*t*-intervals over folds, and dots are individual folds.")

m.h("5.4 Does rice pre-training improve on ImageNet pre-training? (RQ1)", 2)
m.p("This is the primary comparison (Table 9, Fig. 5). For **ConvNeXt-Tiny**, the paired fold-level differences "
    "(ImageNet → rice minus ImageNet, full fine-tuning) were +0.008, −0.011, −0.010 and +0.007 macro-F1 at 10, 25, 50 "
    "and 100 % data. All image-level bootstrap intervals included zero, and no difference met the decision rule. At "
    "25 % the fold-level interval (−0.017 to −0.004, with rice winning in none of the five folds) excludes zero, "
    "which indicates a small deficit. However, fold-level intervals are not corrected for multiplicity, the result "
    "did not meet the bootstrap criterion, and it was not repeated at other fractions. The largest positive estimate, "
    "+0.008 at 10 % (pooled +0.015, 95 % CI −0.005 to +0.036), is within the noise. Balanced accuracy showed the "
    "same lack of pattern (+0.017, −0.031, −0.028, +0.005).", indent=True)
m.p("For **ViT-B/16**, ImageNet → rice scored lower than ImageNet alone at all four fractions: −0.023, −0.022, "
    "−0.031 and −0.016 at the fold level, with rice winning in 1, 2, 1 and 0 of the five folds. The image-level "
    "criterion was met at 10, 50 and 100 % (Holm-adjusted *p* = 0.048, 0.002 and 0.048) but not at 25 % (*p* = "
    "0.063), and every fold-level 95 % interval included zero. The effect is small, about 0.02–0.04 macro-F1. We "
    "regard it as weak evidence that rice pre-training does not help ViT in our setting, and possibly hurts it "
    "slightly, not as an established harm. With a frozen backbone or partial fine-tuning, rice and ImageNet "
    "pre-training were likewise indistinguishable for ConvNeXt (Table 10).", indent=True)
m.p("In short, **we found no evidence that rice intermediate pre-training improves pearl-millet classification over "
    "ImageNet pre-training at any data fraction, for either architecture**. This includes the lowest-data setting of "
    "about 20 training images, where a benefit would be most expected. With five folds, differences smaller than "
    "about 0.04 macro-F1 cannot be ruled out.", indent=True)
h, b = read_md_table(TAB / "T4.md",
                     keep=["Architecture", "Data", "Δ macro-F1 (fold mean)", "d_z", "95 % t-CI (folds)", "Folds won",
                           "Pooled Δ [bootstrap 95 % CI]", "Holm p (bootstrap)", "Verdict"],
                     rename={"Δ macro-F1 (fold mean)": "Δ macro-F1 (folds)", "d_z": "*d*~z~",
                             "95 % t-CI (folds)": "95 % *t*-CI", "Pooled Δ [bootstrap 95 % CI]": "Pooled Δ [bootstrap CI]",
                             "Holm p (bootstrap)": "Holm *p*"},
                     transform=lambda r: r[:4] + [short_ci(r[4])] + r[5:6] + [r[6]] + r[7:8] + [verdict(r[8])])
m.table("Paired comparison, ImageNet → rice minus ImageNet (full fine-tuning). \"Folds won\" counts folds in which "
        "ImageNet → rice scored higher; the verdict follows the decision rule in Section 3.7.", h, b,
        widths_cm=[2.2, 1.2, 1.7, 1.2, 2.5, 1.3, 3.2, 1.3, 1.9], font=8)
m.fig(FIG_V / "fractions_paired_deltas.png",
      "Paired macro-F1 differences. Left: ImageNet → rice minus ImageNet for each architecture. Right: ViT-B/16 minus "
      "ConvNeXt-Tiny for each initialisation. Markers and whiskers show the pooled out-of-fold difference with its "
      "image-level bootstrap 95 % CI; wide pale bars show the fold-level *t*-interval (*n* = 5 folds).")
h, b = read_md_table(TAB / "T10.md",
                     rename={"Δ macro-F1 (fold mean)": "Δ macro-F1 (folds)", "95 % t-CI": "95 % *t*-CI",
                             "Pooled Δ [bootstrap 95 % CI]": "Pooled Δ [bootstrap CI]"},
                     transform=lambda r: r[:3] + [short_ci(r[3])] + r[4:6] + [verdict(r[6])])
m.table("ConvNeXt-Tiny, rice minus ImageNet pre-training for the linear-probe and partial fine-tuning policies.",
        h, b, widths_cm=[1.8, 1.4, 2.4, 3.0, 2.0, 3.6, 2.2], font=8)

m.h("5.5 Rice knowledge without ImageNet (RQ2)", 2)
m.p("Without ImageNet, rice pre-training gave a starting point that transferred, but it was weaker than ImageNet. "
    "Compared with random initialisation (ConvNeXt only), random → rice improved pearl-millet macro-F1 by +0.27 to "
    "+0.31 at every fraction, in all five folds, with bootstrap intervals far from zero (Table 11). Compared with "
    "ImageNet, random → rice was lower at every fraction in both architectures. For ConvNeXt the gap narrowed as data "
    "increased, from −0.160 at 10 % to −0.054 at 100 % (where the fold-level interval includes zero), while for ViT "
    "it stayed between −0.066 and −0.085. ImageNet → rice also scored higher than random → rice at all four fractions "
    "in both architectures. The decision rule was met at all four fractions for ConvNeXt and at 10, 25 and 100 % for "
    "ViT (Appendix Table A2). ImageNet initialisation therefore contributed something beyond what rice supplied.", indent=True)
h, b = read_md_table(TAB / "T5c.md",
                     keep=["Data", "Δ macro-F1 (fold mean)", "d_z", "95 % t-CI (folds)", "Folds won",
                           "Pooled Δ [bootstrap 95 % CI]", "Holm p (bootstrap)", "Verdict"],
                     rename={"Δ macro-F1 (fold mean)": "Δ macro-F1 (folds)", "d_z": "*d*~z~",
                             "95 % t-CI (folds)": "95 % *t*-CI", "Pooled Δ [bootstrap 95 % CI]": "Pooled Δ [bootstrap CI]",
                             "Holm p (bootstrap)": "Holm *p*"},
                     transform=lambda r: r[:3] + [short_ci(r[3])] + r[4:7] + [verdict(r[7])])
m.table("ConvNeXt-Tiny, random → rice minus random initialisation.", h, b,
        widths_cm=[1.4, 2.2, 1.4, 2.8, 1.6, 3.4, 1.6, 2.0], font=8)

m.h("5.6 Architecture comparison (RQ3)", 2)
m.p("Neither architecture was uniformly better (Table 12, Fig. 5 right). With ImageNet initialisation, ViT-B/16 was "
    "lower than ConvNeXt-Tiny at 10 % data (−0.031; bootstrap-supported, fold-level interval −0.060 to −0.002), "
    "indistinguishable at 25 and 50 %, and higher at 100 % (+0.027; the fold-level interval includes zero). With "
    "ImageNet → rice initialisation, ViT was lower at 10 % (−0.062) and indistinguishable otherwise. With random → "
    "rice, ViT was nominally higher at 10–50 % (+0.04 to +0.07), but no comparison met the rule. The sign of the "
    "difference therefore depends on the data fraction and the initialisation. Since ViT-B/16 has three times as many "
    "parameters as ConvNeXt-Tiny, these differences cannot be attributed to the architecture alone, and we make no "
    "claim that either is best.", indent=True)
h, b = read_md_table(TAB / "T5.md",
                     keep=["Initialisation", "Data", "Δ macro-F1 (fold mean)", "d_z", "95 % t-CI (folds)", "Folds won",
                           "Pooled Δ [bootstrap 95 % CI]", "Holm p (bootstrap)", "Verdict"],
                     rename={"Δ macro-F1 (fold mean)": "Δ macro-F1 (folds)", "d_z": "*d*~z~",
                             "95 % t-CI (folds)": "95 % *t*-CI", "Pooled Δ [bootstrap 95 % CI]": "Pooled Δ [bootstrap CI]",
                             "Holm p (bootstrap)": "Holm *p*"},
                     transform=lambda r: r[:4] + [short_ci(r[4])] + r[5:8] + [verdict(r[8])])
m.table("Paired comparison, ViT-B/16 minus ConvNeXt-Tiny (full fine-tuning).", h, b,
        widths_cm=[2.3, 1.2, 1.7, 1.2, 2.5, 1.3, 3.1, 1.3, 1.9], font=8)

m.h("5.7 Per-class performance and the Exserohilum class", 2)
m.p("ImageNet-initialised models classified smut and *S. graminicola* almost perfectly at every fraction (pooled F1 "
    "≥ 0.99), healthy leaves nearly so (0.88–1.00), and *Pyricularia* with F1 0.85–0.92 (Table 13, Fig. 6, Fig. 7). "
    "*Exserohilum*, with only nine images, was unreliable in every condition (pooled F1 0.04–0.38; Table 14), and it "
    "is the main reason macro-F1 stays near 0.8. With ImageNet-initialised ConvNeXt, *Exserohilum* F1 did not "
    "improve with more data (0.31 at both 10 % and 100 %), whereas ImageNet-initialised ViT improved from 0.21 to "
    "0.38. For ViT, rice-initialised models were worse than ImageNet-initialised ones on *Exserohilum* at every "
    "fraction (fold-level F1 difference −0.06 to −0.12), while for ConvNeXt the differences ranged from −0.07 to "
    "+0.02 with no consistent pattern. Differences for the other classes were within ±0.07 and inconsistent in sign.", indent=True)
h, b = read_md_table(TAB / "T6a.md", rename={"exserohilum": "*Exserohilum*", "healthy": "Healthy",
                                             "pyricularia": "*Pyricularia*", "sclerospora": "*Sclerospora*",
                                             "smut": "Smut"})
m.table("Pooled out-of-fold per-class F1 at 100 % data (mean over seeds).", h, b,
        widths_cm=[2.8, 3.0, 2.2, 2.0, 2.2, 2.2, 2.0])
h, b = read_md_table(TAB / "T6c.md")
m.table("*Exserohilum* precision (P), recall (R) and F1, pooled out-of-fold and averaged over seeds.", h, b,
        widths_cm=[2.4, 2.6, 2.85, 2.85, 2.85, 2.85], font=7.5)
m.fig(FIG_V / "arch_confusion_100pct.png",
      "Pooled out-of-fold confusion matrices at 100 % data for both architectures and the three main initialisations. "
      "Cell text gives the mean count per seed; colour is row-normalised. Most errors are *Pyricularia* predicted as "
      "*Exserohilum* and *Exserohilum* predicted as *Pyricularia*.")
m.fig(FIG_V / "fractions_per_class_f1.png",
      "Pooled out-of-fold per-class F1 at each target-data fraction (mean over seeds). \"rice\" denotes ImageNet → rice "
      "and \"ricescratch\" denotes random → rice.")
m.p("**Diagnosis of the hard *Exserohilum* images.** Across all stored runs, three of the nine *Exserohilum* images "
    "(DRECRO_1, _8 and _9) were almost never classified correctly (0–12 % of runs), whereas the other six were "
    "correct in 67–88 % of runs (Fig. 8; Appendix Table A3). For each of the three hard images, the nearest image of "
    "another class (*Pyricularia*) is closer in ImageNet-feature space than the nearest *Exserohilum* image, and a "
    "1-nearest-neighbour classifier in that space labels them *Pyricularia*. Recall is therefore capped at about "
    "6/9 ≈ 0.67, which ImageNet-initialised models reached. Low F1 is also driven by low precision: in the base "
    "ConvNeXt configuration, 23 % of *Pyricularia* images were predicted as *Exserohilum*.", indent=True)
m.p("Inspecting the images suggested a possible cause. The three hard images were photographed against a blue "
    "background, whereas the six easy ones lie on a white or grey surface. A simple check of the image borders "
    "(share of pixels whose blue channel clearly exceeds red and green) confirmed this. All 98 *Pyricularia* images "
    "have a blue background, as do exactly the three misclassified *Exserohilum* images, while none of the healthy or "
    "*S. graminicola* images and 6 of the 75 smut images do. The background is therefore confounded with the "
    "*Pyricularia* label, and the models may use it as a shortcut [@geirhos2020;noyan2022]. The lesions on the three "
    "images also look similar to blast lesions, so the two explanations cannot be separated with these data. We did "
    "not run a background-masking experiment, and we report this observation as a hypothesis for future work, not as "
    "an established cause.", indent=True)
m.fig(FIG_C / "exserohilum_specimens.png",
      "The nine *Exserohilum* images with the share of stored runs that classified each one correctly and the most "
      "frequent predictions. DRECRO_1, _8 and _9, the three that are almost always predicted as *Pyricularia*, are the "
      "only ones photographed against the blue background shared by all *Pyricularia* images.", width_cm=14.5)
m.p("In a controlled exploratory study (Table 15), in which all variants are reported, none was selected on test "
    "performance and none feeds back into the main results, removing class weights raised *Exserohilum* precision "
    "with ImageNet initialisation from 0.20 to 0.46, at lower recall (0.67 → 0.56). Class-balanced sampling and a "
    "higher input resolution (384 pixels) did not help. With nine images, none of these differences is established.", indent=True)
h, b = read_md_table(TAB / "T11.md", rename={"Exserohilum precision": "*Exs.* precision", "recall": "*Exs.* recall",
                                             "F1": "*Exs.* F1", "Pyricularia→Exserohilum": "*Pyr.*→*Exs.*"})
m.table("Exploratory *Exserohilum* study at 100 % data (ConvNeXt-Tiny, 3 seeds, pooled out-of-fold). The \"base\" rows "
        "are re-runs inside the study.", h, b, widths_cm=[2.4, 3.6, 2.0, 1.8, 1.6, 2.4, 2.4], font=8)

m.h("5.8 Calibration", 2)
m.p("All models were **under-confident**. For ViT-B/16 with ImageNet initialisation, mean confidence was 0.74–0.78 "
    "against accuracies of 0.87–0.92, giving a pooled ECE of 0.18–0.24 (Table 16). ConvNeXt per-fold ECE was "
    "similar (0.19–0.24). Random → rice models had lower ECE (0.14–0.16) but also lower accuracy. In a dedicated "
    "ConvNeXt study with a held-out calibration fold (60 % of the data used for training), the under-confidence was "
    "traced to the training loss (Table 17, Fig. 9). Removing label smoothing or class weights reduced pooled ECE "
    "from about 0.20 to 0.06–0.08, and removing both gave 0.05–0.06. Training for longer did not help, and "
    "temperature scaling fitted on the calibration fold lowered ECE to 0.03–0.09. Without label smoothing, the models "
    "became slightly over-confident (mean confidence 0.98 against accuracy 0.91–0.93). Calibration did not differ "
    "materially between ImageNet and ImageNet → rice initialisation.", indent=True)
h, b = read_md_table(TAB / "T7a.md")
h[0] = "Initialisation"
m.table("ViT-B/16 calibration, pooled out-of-fold (mean over 3 seeds).", h, b,
        widths_cm=[2.9, 1.4, 2.0, 2.4, 2.8, 1.6, 1.6])
h, b = read_md_table(TAB / "T7b.md")
m.table("ConvNeXt-Tiny calibration study: models trained on the three folds that are neither the test nor the "
        "calibration fold (60 % of the data); pooled out-of-fold, mean ± SD over 3 seeds.", h, b,
        widths_cm=[4.4, 2.4, 1.4, 1.8, 2.4, 2.6, 1.6], font=8)
m.fig(FIG_C / "calibration_ece_by_variant.png",
      "Pooled out-of-fold ECE in the ConvNeXt-Tiny calibration study, before (raw) and after temperature scaling. "
      "base: label smoothing 0.1 with class weights; ls0: no label smoothing; nobal: no class weights; ls0_nobal: "
      "neither; ep80: base trained for 80 epochs. Error bars are SD over three seeds.")

m.h("5.9 Sensitivity to the number of optimiser steps", 2)
m.p("With a fixed 40 epochs, runs at 10–50 % data take fewer optimiser steps than runs at 100 %. Repeating the "
    "ImageNet-versus-rice comparison with 80 epochs (ConvNeXt, partial and full fine-tuning) did not change the "
    "conclusion. The rice-minus-ImageNet differences were between −0.001 and −0.025, and all fold-level intervals "
    "included zero (Appendix Table A4).", indent=True)

# =========================================================== 6 discussion
m.h("6. Discussion", 1)
m.h("6.1 Intermediate rice pre-training did not help", 2)
m.p("Adding a supervised rice stage after ImageNet did not measurably improve pearl-millet classification at any of "
    "the four data fractions, in either architecture. For ConvNeXt the estimates were within ±0.011 macro-F1. For ViT "
    "they were slightly negative, and every fold-level interval included zero. The result held for frozen and "
    "partially fine-tuned ConvNeXt backbones and when training was doubled in length. Because the lowest-data setting, "
    "about 20 training images, is where plant-specific knowledge should matter most, the absence of any gain there is "
    "the most informative observation.", indent=True)
m.p("This does not mean that rice knowledge is useless. Without ImageNet, rice pre-training produced a far better "
    "starting point than random weights, so the rice features do transfer. They simply did not add to what ImageNet "
    "already provides, and ImageNet-initialised models stayed ahead of rice-only ones at every fraction. Our "
    "experiments cannot tell what the rice features encode, whether generic visual structure that ImageNet also "
    "supplies or lesion-specific cues that ImageNet lacks. Separating these would require an intermediate stage on a "
    "size-matched non-plant dataset, which we did not run.", indent=True)
m.h("6.2 Possible explanations", 2)
m.p("We see four plausible explanations, none of which we tested directly. The first is **little headroom**. "
    "ImageNet-initialised ConvNeXt already reached about 0.80 macro-F1 with 20 images, and smut, *S. graminicola* and "
    "healthy leaves were classified almost perfectly. The remaining error sits in *Exserohilum* and, to a lesser "
    "extent, *Pyricularia*. If three of nine *Exserohilum* images look like *Pyricularia*, whether through their "
    "lesions or their background, no pre-training stage can fix them.", indent=True)
m.p("The second is **domain mismatch**. The rice images are uniform 480×640 photographs, while the pearl-millet "
    "images come from different devices and sizes (most raw images are 4000×3000) and show different backgrounds. If "
    "the rice stage mostly teaches features tied to its own imaging conditions, they may not carry over. The third is "
    "that **the pathogen analogy was not exploited**. If knowledge of related diseases transferred, *Pyricularia* and "
    "*Sclerospora* should have benefited most. They did not: *Pyricularia* differences were close to zero for "
    "ConvNeXt and slightly negative for ViT, and *Sclerospora* was already at ceiling. This is weak, indirect evidence "
    "against a class-specific transfer effect. The fourth is **specific to ViT**. The small deficit for "
    "rice-initialised ViT may reflect the rice stage moving the weights away from useful ImageNet features, or it may "
    "be because the learning rates were set for ConvNeXt and never tuned for ViT. The ViT rice stage itself was "
    "healthy (rice test macro-F1 0.968), so the deficit is not caused by a failed rice stage.", indent=True)
m.h("6.3 The flat data-fraction curve", 2)
m.p("ImageNet-initialised ConvNeXt was nearly insensitive to training-set size, whereas ViT and, much more strongly, "
    "rice-only models improved with more data. A flat curve should be read with care. Macro-F1 is dominated by two hard "
    "classes, the test folds are small (about 45 images), low-fraction runs took fewer optimiser steps, and the 10 % "
    "setting contains only two *Exserohilum* training images. The curve does not show that 20 images are enough in "
    "general. It shows that, on this dataset and with these easy classes, extra images changed the fold-level score "
    "very little.", indent=True)
m.h("6.4 Evaluation protocol, leakage and shortcuts", 2)
m.p("Repeated photographs of the same leaf were spread across the original folds, and removing them lowered every "
    "comparable estimate by 0.06–0.09 macro-F1. Two caveats apply. The specimen groups are inferred from image "
    "features, since no ground-truth plant or leaf identifiers exist, and the 0.93 threshold is our choice. In "
    "addition, the difference between protocols also reflects different fold compositions. We still consider the "
    "grouped protocol the more defensible one, and we recommend that plant-image collections record specimen "
    "identifiers so that splits can be made at the specimen level [@roberts2017;kapoor2023].", indent=True)
m.p("The background finding points to a second, subtler risk. In this collection, every *Pyricularia* image shares a "
    "blue background, so a model can separate *Pyricularia* from most other classes without looking at the lesions. "
    "Specimen grouping cannot remove a confound of this kind, because it is present in every fold. The fact that the "
    "only *Exserohilum* images on a blue background are the ones misclassified as *Pyricularia* is consistent with "
    "shortcut learning [@geirhos2020], as has been reported for PlantVillage [@noyan2022]. It also means that the high "
    "per-class F1 for *Pyricularia* may overstate how well the models recognise blast symptoms. Background "
    "segmentation or masking, and images of every class taken against varied backgrounds, would be needed to resolve "
    "this.", indent=True)
m.h("6.5 Calibration", 2)
m.p("Under the default loss, all models were under-confident, with mean confidence around 0.75 for accuracies around "
    "0.91. The ConvNeXt study traced this to label smoothing combined with effective-number class weights. Label "
    "smoothing lowers the confidence of the network, which helps calibration when a network would otherwise be "
    "over-confident [@muller2019]. In our small-data setting, combined with class weighting, it pushed the models "
    "into under-confidence instead. Removing either one "
    "brought pooled ECE from about 0.20 to 0.06–0.08, and temperature scaling on a held-out calibration fold reduced "
    "it to 0.03–0.09 without touching the test fold. In practice, probabilities from the default configuration should "
    "not be taken at face value, and a post-hoc temperature fitted on held-out data is a cheap remedy [@guo2017].", indent=True)
m.h("6.6 Practical implications", 2)
m.p("For a data-poor crop with a handful of classes, fine-tuning an ImageNet-pre-trained network is a strong "
    "baseline. In our data, an extra stage on a related crop did not justify its cost. Evaluation should be done at the "
    "specimen level, with uncertainty reported over folds, because with a few hundred images differences below about "
    "0.03–0.05 macro-F1 cannot be resolved with five folds. Finally, the largest source of error was a rare, visually "
    "ambiguous class with a possible background confound. More images, expert-verified labels and varied backgrounds "
    "are likely to matter more than the choice of architecture or pre-training.", indent=True)

# =========================================================== 7 limitations
m.h("7. Limitations", 1)
m.p("The conclusions are limited in several ways. The target dataset has 228 images, and the evaluation uses five "
    "folds of 42–49 images. Fold-level comparisons rest on five values, the exact sign-flip test cannot reach "
    "*p* < 0.05, and differences of roughly ±0.03–0.05 macro-F1 could not be excluded. The decision rule was fixed in "
    "advance, but the choice of comparison families was ours, many comparisons were exploratory, and several "
    "\"supported\" verdicts, such as rice-initialised ViT scoring below ImageNet-initialised ViT, have fold-level "
    "intervals that include zero. These should be treated as suggestive.", indent=True)
m.p("*Exserohilum rostratum* has nine images, distributed 1/1/1/1/5 across folds, so its per-class scores change "
    "substantially with a single image. We cannot tell whether the three hard images are mislabelled, atypical, true "
    "look-alikes or affected by the background confound. All per-class conclusions about this class are unreliable. "
    "The specimen groups are inferred, not observed, and the grouped folds still leave moderately similar images across "
    "folds (62 % of test images at cosine ≥ 0.90). We used a single fold assignment, chosen by label and group balance "
    "only, and did not repeat the grouped cross-validation with other shuffles. The data come from one source, with "
    "limited variation in site, device and season, and there is no external test set or field validation, so the "
    "results say nothing about deployment.", indent=True)
m.p("The pearl-millet stage used a fixed 40 epochs without checkpoint selection, and no hyper-parameter was tuned on "
    "pearl-millet data. This avoids selection on the test set but may disadvantage the architecture for which the "
    "settings suit less well, most likely ViT. ViT-B/16 is three times larger than ConvNeXt-Tiny and lacks stochastic "
    "depth, and the intended size-matched DeiT-Small could not be used. ViT was run with full fine-tuning only and "
    "without a random-initialisation baseline, and the calibration, *Exserohilum*, transfer-policy and steps-matched "
    "studies used ConvNeXt only. We used one source dataset and one rice recipe, without varying the length of the "
    "rice stage. Pooled calibration values were available only for ViT, because the ConvNeXt fraction runs did not "
    "save logits. Finally, runs were deterministic on our hardware, which does not guarantee bit-identical results "
    "elsewhere.", indent=True)

# =========================================================== 8 conclusion
m.h("8. Conclusion and future work", 1)
m.p("We tested whether intermediate pre-training on rice-disease images improves pearl-millet disease "
    "classification over ImageNet pre-training. We used a specimen-grouped evaluation, two architectures and four "
    "target-data fractions. Within the limits of a 228-image dataset and five folds, rice pre-training did not "
    "measurably improve on ImageNet at any fraction, for ConvNeXt-Tiny or ViT-B/16, and there was no sign of a "
    "benefit in the lowest-data setting of about 20 training images. Rice knowledge does transfer, since rice-only "
    "pre-training was far better than random initialisation, but it does not replace ImageNet. Neither architecture "
    "was uniformly better. The evaluation protocol mattered: repeated photographs of the same leaf inflated scores "
    "by 0.06–0.09 macro-F1, and a background shared by all *Pyricularia* images may act as a shortcut. The remaining "
    "error is concentrated in one rare and ambiguous class, and the under-confidence of the models is explained by "
    "the loss settings and largely repaired by temperature scaling.", indent=True)
m.p("These findings apply to this dataset, recipe and pair of architectures. They do not show that related-crop "
    "pre-training is ineffective in general. Future work should repeat the grouped cross-validation with several fold "
    "assignments; add a size-matched transformer and a second convolutional network; include control datasets for the "
    "intermediate stage, both non-plant and pathogen-matched; test background masking; have the *Exserohilum* "
    "images reviewed by a plant pathologist and collect more of them; and evaluate on an external test set from a "
    "different site or device.", indent=True)

# =========================================================== declarations
m.h("Declarations", 1)
m.p("**Author contributions.** {{HL:[Authors to confirm the split of work.]}} Zahid Rashid: conceptualisation, "
    "methodology, software, formal analysis, writing (original draft). Shawal Nasir: data curation, validation, "
    "visualisation, writing (review and editing). Both authors read and approved the final manuscript.", align="justify")
m.p("**Funding.** {{HL:[Authors to confirm.]}} This research received no specific grant from any funding agency in "
    "the public, commercial or not-for-profit sectors.")
m.p("**Competing interests.** {{HL:[Authors to confirm.]}} The authors declare no competing interests.")
m.p("**Data availability.** The pearl-millet images are available from Zenodo [@pm_dataset], and the Paddy Doctor "
    "rice images from Kaggle [@paddydoctor_kaggle], subject to the competition rules. The cleaned manifests, fold "
    "assignments and per-run results are available from the corresponding author on request "
    "{{HL:[or give a repository link]}}.")
m.p("**Code availability.** {{HL:[Authors to decide: repository link, or available on request.]}}")
m.p("**Acknowledgements.** We thank the creators of the pearl-millet and Paddy Doctor datasets for making their "
    "images publicly available.")

# =========================================================== appendix
m.h("Appendix A. Supplementary tables", 1)
_tab_before = m.tab_n


def appendix_table(label, caption, header, rows, **kw):
    """Appendix tables are numbered A1, A2 … instead of continuing the main sequence."""
    from docx.shared import Pt
    cap = m.doc.add_paragraph()
    cap.paragraph_format.keep_with_next = True
    r = cap.add_run(f"Table {label}. ")
    r.bold = True
    r.font.size = Pt(9.5)
    m.runs(cap, caption, size=9.5)
    t_caption_skip(header, rows, **kw)


def t_caption_skip(header, rows, widths_cm=None, font=8.5):
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Pt
    n = len(header)
    t = m.doc.add_table(rows=1 + len(rows), cols=n)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    widths_cm = widths_cm or [16.4 / n] * n
    for ri, row in enumerate([header] + rows):
        for ci, val in enumerate(row):
            cell = t.rows[ri].cells[ci]
            cell.width = Cm(widths_cm[ci])
            para = cell.paragraphs[0]
            para.paragraph_format.space_after = Pt(1)
            para.paragraph_format.line_spacing = 1.0
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
            m.runs(para, str(val), size=font, bold=(ri == 0))
    m._three_line(t)
    m.doc.add_paragraph()


h, b = read_md_table(TAB / "T3c.md")
appendix_table("A1", "Accuracy (mean ± SD over folds) by target-data fraction.", h, b,
               widths_cm=[2.8, 3.0, 2.65, 2.65, 2.65, 2.65])
h, b = read_md_table(TAB / "T5b.md",
                     keep=["Comparison", "Data", "Δ macro-F1 (fold mean)", "95 % t-CI (folds)", "Folds won",
                           "Pooled Δ [bootstrap 95 % CI]", "Holm p (bootstrap)", "Verdict"],
                     rename={"Δ macro-F1 (fold mean)": "Δ macro-F1 (folds)", "95 % t-CI (folds)": "95 % *t*-CI",
                             "Pooled Δ [bootstrap 95 % CI]": "Pooled Δ [bootstrap CI]", "Holm p (bootstrap)": "Holm *p*"},
                     transform=lambda r: r[:3] + [short_ci(r[3])] + r[4:7] + [verdict(r[7])])
appendix_table("A2", "Secondary paired comparisons (first minus second).", h, b,
               widths_cm=[4.2, 1.2, 1.7, 2.5, 1.3, 3.1, 1.3, 1.9], font=7.5)
h, b = read_md_table(TAB / "T12.md")
appendix_table("A3", "The nine *Exserohilum* images: share of stored runs classifying each correctly, and "
               "ImageNet-feature cosine similarity to the nearest same-class and other-class image.", h, b,
               widths_cm=[2.4, 3.6, 3.4, 3.4, 3.4])
h, b = read_md_table(TAB / "T9.md", transform=lambda r: r[:5] + [r[5].replace(" [", " ["), r[6]])
appendix_table("A4", "ConvNeXt-Tiny, rice minus ImageNet with 40 and 80 epochs (specimen-grouped folds).", h, b,
               widths_cm=[2.6, 1.6, 1.4, 1.9, 2.4, 4.4, 2.1], font=8)

# =========================================================== references
m.references()
unused = m.save(OUT)
print("saved", OUT)
print("figures", m.fig_n, "tables", _tab_before, "citations", len(m.order))
if unused:
    print("UNUSED reference keys:", unused)

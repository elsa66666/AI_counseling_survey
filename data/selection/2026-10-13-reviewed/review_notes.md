# Per-paper eligibility review

Snapshot: 2026-10-13-reviewed · protocol: selection-v1.1

This is one AI eligibility review, separate from the saved three-agent SFPE labels. Reasons are paraphrases of method evidence; publisher PDFs are linked and hashed, not redistributed. One Woebot HTML source has no archived response hash. Original GPT discovery logs and exact reviewer model identifier are unavailable.



## ELIZA---A Computer Program for the Study of Natural Language Communication Between Man and Machine

`weizenbaum1966eliza` · **COUNSELOR / Included** · Historical non-LLM

Implements a DOCTOR script that imitates a Rogerian psychotherapist using ranked keywords and transformation rules. This is a historical counselor-role model, without an efficacy requirement.

DOCTOR 脚本用关键词和转换规则模拟心理治疗师，符合咨询师角色标准；技术上单列为历史非 LLM 系统。

Evidence: DOCTOR script and transformation rules; PDF pp.1–2 — [reviewed source](https://web.stanford.edu/class/cs124/p36-weizenabaum.pdf)

Publication: Crossref publisher-deposited record matches title; type=journal-article; venue=Communications of the ACM; publication date=[1966, 1, 1]; DOI=10.1145/365153.365168 — [record](https://api.crossref.org/works/10.1145%2F365153.365168)

Boundary: Historical method; eligible role does not imply therapeutic efficacy.

Source SHA-256: `d0c58989bff11741aec3fbf52a49b3dcd0ede45ebabfa249815602b81ef07c1a`



## Establishing and Maintaining Long-Term Human--Computer Relationships

`bickmore2005relationships` · **SUPPORT / Supporting** · Historical non-LLM

FitTrack is a scripted exercise-adoption advisor. The implemented target is physical-activity behavior, without an explicit mental-health-support or MI counseling process. Retain as conceptual background on relational agents and working alliance.

FitTrack 的具体任务是运动习惯建议，未实现明确的心理支持或 MI 咨询过程；作为关系型代理和工作联盟的背景文献保留。

Evidence: §6–6.1 FitTrack; author manuscript PDF pp.18–20 — [reviewed source](https://relationalagents.com/publication/2005/establishing-and-maintaining-long-term-human-computer-relationships/05_CHI_BTPR.pdf)

Publication: Crossref publisher-deposited record matches title; type=journal-article; venue=ACM Transactions on Computer-Human Interaction; publication date=[2005, 6]; DOI=10.1145/1067860.1067867 — [record](https://api.crossref.org/works/10.1145%2F1067860.1067867)

Boundary: Behavior change alone does not establish mental-health counseling; explicit MI counseling is eligible.

Source SHA-256: `5faef57e8e4c54b0e7236f2eceeb2b7e6f3162d6c14e45661bb8fc2dd857a56d`



## Delivering Cognitive Behavior Therapy to Young Adults With Symptoms of Depression and Anxiety Using a Fully Automated Conversational Agent (Woebot): A Randomized Controlled Trial

`fitzpatrick2017woebot` · **COUNSELOR / Included** · Historical non-LLM

Woebot delivers daily CBT-oriented conversations and mood tracking through a decision tree with NLP routing, mood-dependent support, goal tracking and reflection. It directly implements mental-health support.

Woebot 通过决策树与 NLP 路由提供 CBT 对话、情绪追踪和个性化支持，属于心理支持模型。

Evidence: Methods → Interventions → Woebot; publisher HTML paragraphs on decision tree, tailoring, goals and reflection — [reviewed source](https://mental.jmir.org/2017/2/e19/)

Publication: Crossref publisher-deposited record matches title; type=journal-article; venue=JMIR Mental Health; publication date=[2017, 6, 6]; DOI=10.2196/mental.7785 — [record](https://api.crossref.org/works/10.2196%2Fmental.7785)

Boundary: Clinical trial papers qualify when the intervention itself implements an eligible role.

Source SHA-256: `not archived (HTML source)`



## Towards Empathetic Open-domain Conversation Models: A New Benchmark and Dataset

`rashkin-etal-2019-towards` · **SUPPORT / Supporting** · Pretrained neural language model

The Listener models generate empathetic replies to personal situations spanning positive and negative emotions. The stated task is open-domain empathy rather than counseling or distress-relief support. Retain the dataset and empathy modeling as foundational supporting literature.

其任务是开放域情境中的共情回应，并未明确建模心理咨询或缓解困扰的支持过程；作为基础数据集与共情研究保留。

Evidence: §3 collection and §4 Empathetic Response Generation; PDF pp.4–5 — [reviewed source](https://aclanthology.org/P19-1534.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics; date=2019/7 — [record](https://aclanthology.org/P19-1534/)

Boundary: A generative model is not sufficient without an explicit counseling/support purpose.

Source SHA-256: `cc0947d2f3be24d2ee8b6b1cca70463036d5d981d45416088eb621060d554b60`



## Towards Emotional Support Dialog Systems

`liu-etal-2021-towards` · **COUNSELOR / Included** · Pretrained neural language model

Defines emotional-support stages and strategies and trains strategy-aware BlenderBot/DialoGPT variants to generate supporter responses that alleviate help-seeker distress.

除 ESConv 数据集外，还训练策略感知的支持者回应模型，目标是缓解求助者情绪困扰，因此纳入。

Evidence: §3.2 ESC Framework; §6.1–6.2 model variants; PDF pp.4,7 — [reviewed source](https://aclanthology.org/2021.acl-long.269.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers); date=2021/8 — [record](https://aclanthology.org/2021.acl-long.269/)

Boundary: A resource paper with a trained support model qualifies.

Source SHA-256: `673cdbeb992ecd535bbb5b7b598b5ab16e8c130d517a66b8e19cb479cb5cbbdc`



## PsyQA: A Chinese Dataset for Generating Long Counseling Text for Mental Health Support

`sun-etal-2021-psyqa` · **COUNSELOR / Included** · Pretrained neural language model

Trains psychology-domain GPT-2 and strategy-conditioned counseling-text generators from question/context input. This implements support generation in addition to releasing PsyQA.

不仅发布 PsyQA，也训练以问题和策略为条件的心理支持文本生成模型。

Evidence: §6.2–6.3 counseling-text model training; PDF p.7 — [reviewed source](https://aclanthology.org/2021.findings-acl.130.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021; date=2021/8 — [record](https://aclanthology.org/2021.findings-acl.130/)

Boundary: Long single-turn support qualifies; no minimum turn count.

Source SHA-256: `22f418a86f6280fa13165e74c5ebd1b9a934d2fb6e5f501137232cd0dd4a9708`



## Improving Multi-turn Emotional Support Dialogue Generation with Lookahead Strategy Planning

`cheng-etal-2022-improving` · **COUNSELOR / Included** · Pretrained neural language model

MultiESC models user states, plans support strategies with lookahead user-feedback prediction, and decodes the selected strategy into the next supportive utterance.

MultiESC 根据用户状态与预测反馈规划支持策略，并生成下一轮回应。

Evidence: §4 Methodology and §4.4 decoder; PDF pp.3,6 — [reviewed source](https://aclanthology.org/2022.emnlp-main.195.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing; date=2022/12 — [record](https://aclanthology.org/2022.emnlp-main.195/)

Boundary: Predicting feedback is not a standalone simulated client role.

Source SHA-256: `d1d58736c91472c0666630659aa5613218e579e329645299d97aa7a6cb5e922f`



## Understanding Client Reactions in Online Mental Health Counseling

`li-etal-2023-understanding` · **SUPPORT / Supporting** · Pretrained neural language model

Provides a client/counselor behavior taxonomy, annotated counseling conversations, outcome correlations and retrospective classifiers. It labels observed utterances rather than generating client behavior or selecting new counselor actions.

提供行为分类体系、标注、相关性分析及事后分类器；没有生成来访者行为或新的咨询师行动。

Evidence: §3 annotation framework; §5.4 automatic label prediction; PDF pp.3,8 — [reviewed source](https://aclanthology.org/2023.acl-long.577.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2023/7 — [record](https://aclanthology.org/2023.acl-long.577/)

Boundary: Detecting a client state does not itself simulate the client.

Source SHA-256: `de1261e82fc9eb96a652cb61ac9ee47ec767af75c266b07b048e4c66d742c1b7`



## TransESC: Smoothing Emotional Support Conversation via Turn-Level State Transition

`zhao-etal-2023-transesc` · **COUNSELOR / Included** · Pretrained neural language model

TransESC encodes semantic, strategy and emotion transitions and injects them into a transition-aware decoder to generate emotional-support responses.

TransESC 将语义、策略与情绪转换信息注入解码器，生成情绪支持回应。

Evidence: §4 Methodology; PDF p.3 — [reviewed source](https://aclanthology.org/2023.findings-acl.420.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2023; date=2023/7 — [record](https://aclanthology.org/2023.findings-acl.420/)

Boundary: Turn-state representations describe the support system, not a separate client simulator.

Source SHA-256: `867c5f7dd782a5e0d9583dff08d534a913d69cd89a79c7beb85701b05f1788b9`



## Knowledge-Enhanced Mixed-Initiative Dialogue System for Emotional Support Conversations

`deng-etal-2023-knowledge` · **COUNSELOR / Included** · Pretrained neural language model

KEMI retrieves counseling knowledge and jointly generates mixed-initiative supportive responses and strategy decisions from the current user utterance and context.

KEMI 检索心理支持知识并生成混合主动性策略与回应。

Evidence: §4 Method and §4.1 Knowledge Acquisition; PDF p.5 — [reviewed source](https://aclanthology.org/2023.acl-long.225.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2023/7 — [record](https://aclanthology.org/2023.acl-long.225/)

Boundary: A knowledge component qualifies through its implemented support-generation use.

Source SHA-256: `92f80e6fdbcab82f353f971b61157b2014597f99caf9eca8a27f7ed895ce67b7`



## Facilitating Multi-turn Emotional Support Conversation with Positive Emotion Elicitation: A Reinforcement Learning Approach

`zhou-etal-2023-facilitating` · **COUNSELOR / Included** · Pretrained neural language model

SUPPORTER selects expert actions from dialogue state and optimizes supportive response generation with emotion-elicitation and coherence rewards.

SUPPORTER 根据对话状态选择专家行动，并用情绪改善与连贯性奖励优化支持回应。

Evidence: §4 Methodology; PDF p.3 — [reviewed source](https://aclanthology.org/2023.acl-long.96.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2023/7 — [record](https://aclanthology.org/2023.acl-long.96/)

Boundary: Reward prediction is not client simulation.

Source SHA-256: `0bd289a223d7ab9e6c8ca0ee4fd2108adc8435df7c4149cc85f2c54c58476a74`



## SoulChat: Improving LLMs' Empathy, Listening, and Comfort Abilities through Fine-Tuning with Multi-turn Empathy Conversations

`chen-etal-2023-soulchat` · **COUNSELOR / Included** · LLM

Fine-tunes ChatGLM-6B to generate the next psychologist response conditioned on multi-turn user–psychologist dialogue history.

微调 ChatGLM-6B，根据多轮咨询历史生成下一条心理咨询师回应。

Evidence: §2.2 SoulChat Model and §3.2 fine-tuning; PDF pp.3–4 — [reviewed source](https://aclanthology.org/2023.findings-emnlp.83.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: EMNLP 2023; date=2023/12 — [record](https://aclanthology.org/2023.findings-emnlp.83/)

Boundary: Synthetic training dialogues alone are not a client simulator.

Source SHA-256: `1934517242b1e041785e69ceda357d13354c1166fb59d45e07ab3afa3d27ecd1`



## Human--AI Collaboration Enables More Empathic Conversations in Text-Based Peer-to-Peer Mental Health Support

`sharma2023hailey` · **COUNSELOR / Included** · Pretrained neural language model

HAILEY presents generated insert/replace suggestions from the PARTNER empathic-rewriting model to peer supporters during mental-health support writing. The human retains control, but the model directly adapts the support response.

HAILEY 在心理支持写作中生成插入或替换建议，直接改写支持回应；人工保留控制权不影响其纳入资格。

Evidence: Methods → Feedback Workflow; author preprint PDF pp.14–15; Supplementary Table S1 p.22 — [reviewed source](https://arxiv.org/pdf/2203.15144)

Publication: Publisher citation metadata matches title; venue=Nature Machine Intelligence; date=2023/01 — [record](https://www.nature.com/articles/s42256-022-00593-2)

Boundary: Human-in-the-loop response assistance qualifies; author preprint reviewed separately from publication proof.

Source SHA-256: `14bf9951694ef23952b069c5426670cce2151518bc6236d6fd3a7e35a1aae092`



## CPsyCoun: A Report-Based Multi-turn Dialogue Reconstruction and Evaluation Framework for Chinese Psychological Counseling

`zhang-etal-2024-cpsycoun` · **COUNSELOR / Included** · LLM

Fine-tunes InternLM2-7B-Chat on reconstructed counseling dialogues to obtain CPsyCounX, a psychological counseling chat model. Memo2Demo transcript reconstruction alone is not the qualifying client role.

训练并评估心理咨询聊天模型 CPsyCounX，因此纳入；整段对话重建本身不算独立来访者模拟。

Evidence: §4.3 Extrinsic Evaluation → CPsyCounX; PDF p.7 — [reviewed source](https://aclanthology.org/2024.findings-acl.830.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2024; date=2024/8 — [record](https://aclanthology.org/2024.findings-acl.830/)

Boundary: Saved SFPE auditors name different targets (Memo2Demo/CPsyCounX); paper eligibility does not resolve that alignment.

Source SHA-256: `69c23bdd053d37fe992ccd8947c16a0d57eeb26f7082077569bf4637e2130261`



## SMILE: Single-turn to Multi-turn Inclusive Language Expansion via ChatGPT for Mental Health Support

`qiu-etal-2024-smile` · **COUNSELOR / Included** · LLM

Beyond offline QA-to-dialogue expansion, trains a ChatGLM2-6B supporter to predict the next support utterance from the dialogue history using supervised LoRA fine-tuning.

除离线对话扩展外，还微调 ChatGLM2-6B 来预测下一轮支持者回应。

Evidence: §6 Dialogue System, §6.1–6.2; PDF p.7 — [reviewed source](https://aclanthology.org/2024.findings-emnlp.34.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: EMNLP 2024; date=2024/11 — [record](https://aclanthology.org/2024.findings-emnlp.34/)

Boundary: Whole-transcript expansion is not interactive client simulation.

Source SHA-256: `ca7dfc4581f3bea0eb052d13fe672381a9b429c0416e0d27f5607babef911e0c`



## HealMe: Harnessing Cognitive Reframing in Large Language Models for Psychotherapy

`xiao-etal-2024-healme` · **COUNSELOR / Included** · LLM

Trains LLaMA2-7B-chat as HealMe for cognitive-reframing psychotherapy conversations and evaluates its responses with real-person clients.

训练 HealMe 进行认知重构心理支持对话，并评估其咨询回应。

Evidence: §5 Training and §6 Experiments; PDF p.5 — [reviewed source](https://aclanthology.org/2024.acl-long.93.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2024/8 — [record](https://aclanthology.org/2024.acl-long.93/)

Boundary: Real-person evaluation is evidence about the model, not an eligibility prerequisite.

Source SHA-256: `d0af5bfeb32ef766a6a73a98ce2bd9716a55b60e225e2775c1d1db213a8925db`



## Cactus: Towards Psychological Counseling Conversations Using Cognitive Behavioral Theory

`lee-etal-2024-cactus` · **BOTH / Included** · LLM

Constructs profile/attitude-conditioned AI clients for multi-turn CounselingEval and trains CAMEL to choose CBT techniques, plan counseling and conduct sessions. Both counselor and client roles are implemented.

既设计画像和态度控制的 AI 来访者用于多轮评估，又训练 CAMEL 选择 CBT 技术和开展咨询，标为双角色。

Evidence: §4.1 CounselingEval and §4.2 CAMEL; PDF pp.5–7 — [reviewed source](https://aclanthology.org/2024.findings-emnlp.832.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: EMNLP 2024; date=2024/11 — [record](https://aclanthology.org/2024.findings-emnlp.832/)

Boundary: Evaluation does not exclude a paper implementing its own client setup; count the paper once.

Source SHA-256: `426f0defa8f4ab9a1c253d2dec7b621b8ff0330d98a8944af100ab5973b661dd`



## PsyGUARD: An Automated System for Suicide Detection and Risk Assessment in Psychological Counseling

`qiu-etal-2024-psyguard` · **SUPPORT / Supporting** · LLM and pretrained neural classifiers

Trains and prompts models to assign suicide-risk labels to observed counseling utterances. Its reported computational output is risk classification, rather than a generated support response, intervention policy or simulated client.

报告的模型输出是咨询话语的自杀风险类别，没有实现支持回应、干预策略或来访者模拟，另列支持文献。

Evidence: §5 Automated System for Suicide Detection; PDF pp.6–7 — [reviewed source](https://aclanthology.org/2024.emnlp-main.264.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing; date=2024/11 — [record](https://aclanthology.org/2024.emnlp-main.264/)

Boundary: Risk relevance and an automated-system title do not by themselves establish counselor generation.

Source SHA-256: `723d211ba8d7814646045905d6bf0c82a699dc5670c577051d250692ec97b369`



## CAMI: A Counselor Agent Supporting Motivational Interviewing through State Inference and Topic Exploration

`yang-etal-2025-cami` · **COUNSELOR / Included** · LLM

CAMI infers client state, explores topics, chooses MI strategies and ranks candidate counselor responses. Its experiments reuse a separately proposed client simulation framework; the contribution assessed here is the counselor agent.

CAMI 推断来访者状态、探索话题、选择 MI 策略并排序咨询师回应；实验复用已有模拟器，核心贡献归咨询师。

Evidence: §3.4 Response Generation & Ranking; §4.1 client implementation provenance; PDF p.5 — [reviewed source](https://aclanthology.org/2025.acl-long.1024.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2025/7 — [record](https://aclanthology.org/2025.acl-long.1024/)

Boundary: Reusing a published simulator as an evaluation tool does not add a new client-model contribution.

Source SHA-256: `1287bfba6be957f3c620277b398576b7297229c64628a83c2c51af998220e67e`



## Can You Share Your Story? Modeling Clients' Metacognition and Openness for LLM Therapist Evaluation

`kim-etal-2025-story` · **CLIENT / Included** · LLM

MindVoyager controls a simulated client’s metacognition and openness by masking/unmasking its cognitive diagram during interaction. The therapist models are evaluated systems, not the proposed modeling role.

MindVoyager 通过逐步开放认知图控制模拟来访者的元认知和开放性，属于来访者模型。

Evidence: §3.1–3.2 MindVoyager; PDF pp.3–4 — [reviewed source](https://aclanthology.org/2025.findings-acl.1332.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2025; date=2025/7 — [record](https://aclanthology.org/2025.findings-acl.1332/)

Boundary: Client cognitive diagrams must not be interpreted as counselor-side formulation.

Source SHA-256: `8a794ccd42c6efd2e6741598f66fcb1ef7cb9376746e6c28063bf51342ad9716`



## PsyDial: A Large-Scale Long-Term Conversational Dataset for Mental Health Support

`qiu-lan-2025-psydial` · **COUNSELOR / Included** · LLM

Trains counseling-response models on reconstructed privacy-preserving PsyDial dialogues. Masked client-utterance reconstruction is offline corpus construction rather than a separately interacting client policy.

在重建数据上训练咨询回应模型；离线填补被遮蔽的来访者话语并不等同交互式模拟器。

Evidence: §4 reconstruction and §6.1.1 backbone training; PDF pp.4,6 — [reviewed source](https://aclanthology.org/2025.acl-long.1049.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2025/7 — [record](https://aclanthology.org/2025.acl-long.1049/)

Boundary: Eligibility derives from trained counselor models, not merely releasing reconstructed data.

Source SHA-256: `b6af3a996e31f0d00c791ca55e3b0f28a5c148aa3cad9100c9e97511fa95b282`



## Randomized Trial of a Generative AI Chatbot for Mental Health Treatment

`heinz2025therabot` · **COUNSELOR / Included** · LLM

Therabot fine-tunes decoder models on therapist–patient support dialogue and delivers generative mental-health treatment conversations in the reported randomized trial.

Therabot 微调解码模型并实际提供生成式心理支持对话，符合咨询师角色。

Evidence: Methods → Model Training and Inference; PDF p.3 — [reviewed source](https://gwern.net/doc/psychiatry/depression/2025-heinz.pdf)

Publication: Crossref publisher-deposited record matches title; type=journal-article; venue=NEJM AI; publication date=[2025, 3, 27]; DOI=10.1056/aioa2400802 — [record](https://api.crossref.org/works/10.1056%2FAIoa2400802)

Boundary: Clinical outcomes do not establish internal SFPE dependencies.

Source SHA-256: `cc8eb0d339bc300d45c5efde810fe870cff1c920a84dcb620f33c07c95498d1c`



## From Generic Empathy to Personalized Emotional Support: A Self-Evolution Framework for User Preference Alignment

`ye-etal-2025-generic` · **COUNSELOR / Included** · LLM

Trains an emotional-support model on ESConv and iteratively optimizes personalized supporter responses through synthetic preference pairs and self-reflection on user preferences.

通过 ESConv 与偏好优化训练个性化情绪支持回应模型。

Evidence: §2.1–2.2 self-evolution and preference optimization; PDF pp.2–3 — [reviewed source](https://aclanthology.org/2025.findings-emnlp.1024.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: EMNLP 2025; date=2025/11 — [record](https://aclanthology.org/2025.findings-emnlp.1024/)

Boundary: User-preference inference and offline query reuse do not implement a client simulator.

Source SHA-256: `89c6fab66cdd7b1b8a6af638ec30e1c1b8cff308363c0e844d25ac1008f28ddf`



## MIRROR: Multimodal Cognitive Reframing Therapy for Rolling with Resistance

`kim-etal-2025-mirror` · **BOTH / Included** · LLM / vision-language model

Implements planning/emotional-captioning therapist variants trained on MIRROR and a profile-conditioned resistant virtual client with turn-dependent nonverbal cues and facial-image generation for interactive sessions.

既实现咨询模型的规划与情绪图像推理，也设计带阻抗画像及逐轮非语言线索的虚拟来访者，归双角色。

Evidence: §4 reasoning; §5.1 resistant clients and §5.2 therapist variants; PDF pp.5–6 — [reviewed source](https://aclanthology.org/2025.emnlp-main.751.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing; date=2025/11 — [record](https://aclanthology.org/2025.emnlp-main.751/)

Boundary: Dedicated interactive resistant clients qualify; offline screenplay generation alone would not.

Source SHA-256: `df95434c43bb9ced876b07500ec315557702af7ffb0a9b6e4cab65a60909512c`



## StoryMI: Steerable Multi-Agent Therapeutic Dialogue Generation

`meng-etal-2026-storymi` · **BOTH / Included** · LLM

Client and therapist agents alternately generate utterances; an interaction manager selects MI strategies, synchronizes shared dialogue state and controls termination. Both roles are explicitly modeled in the proposed workflow.

客户端与治疗师代理交替生成话语，管理代理选择 MI 策略并更新状态，明确建模双角色。

Evidence: §3.3 and Algorithm 1 MI-Coded Dialogue Generation; PDF pp.3–4 — [reviewed source](https://aclanthology.org/2026.findings-acl.468.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2026; date=2026/7 — [record](https://aclanthology.org/2026.findings-acl.468/)

Boundary: A coordinated turn-by-turn simulation qualifies even when its output is a dataset.

Source SHA-256: `af4f2a6baf5404e1440855c3f9c9d92daab9a2d679e1efca7fee91666e29851b`



## Interactive Agents: Simulating Counselor--Client Psychological Counseling via Role-Playing LLM-to-LLM Interactions

`qiu-lan-2026-interactive` · **BOTH / Included** · LLM

Implements role-card-conditioned LLM clients interacting turn by turn with LLM counselors, evaluates both roles and uses the generated sessions to train counselor models.

基于角色卡模拟来访者并与咨询师代理逐轮互动，分别评估两种角色并训练咨询模型。

Evidence: §3.1–3.2 task formulation and §3.6 implementation; PDF pp.3,5 — [reviewed source](https://aclanthology.org/2026.starsem-conference.29.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 15th Joint Conference on Lexical and Computational Semantics (*SEM 2026); date=2026/7 — [record](https://aclanthology.org/2026.starsem-conference.29/)

Boundary: Interactive generation differs from single-call whole-transcript reconstruction.

Source SHA-256: `a80b7ac81650523462a068d84976c031b4d9d639f9eca1d5980ec177446807d4`



## Psychological Counseling Cannot Be Achieved Overnight: Automated Psychological Counseling Through Multi-Session Conversations

`wang-etal-2026-psychological` · **COUNSELOR / Included** · LLM

Trains MusPsy-Model to extract session memory, plan next-session goals and provide counseling responses across multiple sessions. Offline multi-session screenplay generation is a construction step.

训练 MusPsy-Model 抽取会谈记忆、规划后续目标并提供多次会谈回应；离线剧本生成单列为数据构建。

Evidence: §3.4 Memory Generation and §6.1 MusPsy-Model; PDF pp.5,7 — [reviewed source](https://aclanthology.org/2026.findings-acl.818.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2026; date=2026/7 — [record](https://aclanthology.org/2026.findings-acl.818/)

Boundary: Cross-session support qualifies; constructing client profiles alone is not client modeling.

Source SHA-256: `e077a55d0017eb64b5f5de6537eae2f942b7eefc799d8a4c2d8da906775d735d`



## TRACE: Two-Phase RL for Causal Graph Exploration and Deeper Psychological Intervention in Dynamic Counseling Scenarios

`tang-etal-2026-trace` · **COUNSELOR / Included** · LLM

TRACE optimizes a counselor policy to explore the client’s cognitive causal graph before generating cognitive interventions. The closed-source profile-prompted client is an environment tool; no dedicated new client-model method is assessed.

TRACE 优化咨询师先探索认知因果图、再干预的策略；画像提示客户端作为训练环境工具，不另记新的模拟器贡献。

Evidence: §4.1–4.3 two-phase counselor RL; PDF p.4 — [reviewed source](https://aclanthology.org/2026.findings-acl.1711.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2026; date=2026/7 — [record](https://aclanthology.org/2026.findings-acl.1711/)

Boundary: The saved four-node code remains subject to its original consistency flag.

Source SHA-256: `dd47d87259242115fdd2a32a29c317041820694f34016bfb61ac1c0d26e03dde`



## Cognitive Policy-Driven LLM for Diagnosis and Intervention of Cognitive Distortions in Emotional Support Conversation

`zhong-etal-2026-cognitive` · **COUNSELOR / Included** · LLM

Learns counselor intervention strategies with DQN and distills diagnostic and strategy-aligned response targets into an LLM. A distortion-conditioned seeker supplies the training environment; the proposed role-modeling target is the counselor policy.

用 DQN 学习咨询干预策略，并将诊断和策略一致的回应蒸馏到 LLM，主要建模咨询师策略。

Evidence: §4.1 CPRL and §4.2 DSCO; PDF pp.5–6 — [reviewed source](https://aclanthology.org/2026.acl-long.806.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2026/7 — [record](https://aclanthology.org/2026.acl-long.806/)

Boundary: An auxiliary prompt-based seeker does not establish a separately proposed simulator contribution.

Source SHA-256: `5d3ab968ec670fdde4c911dd74e989b195f07d3b8cf85c5870f3313ba000776d`



## MIThinker: A Plug-and-Play Policy-Optimized Thinker For Motivational Interviewing Counseling

`yang-etal-2026-mithinker` · **COUNSELOR / Included** · LLM

Trains a thinker to generate MI-specific counselor thoughts that condition the counselor’s response; the evaluation uses the previously published consistent-client simulation framework.

训练 MI 思考模块来控制咨询师回应，评估复用已有来访者模拟方法。

Evidence: §3.3 MIThinker fine-tuning and §4.1 reused simulator; PDF pp.4–5 — [reviewed source](https://aclanthology.org/2026.findings-acl.163.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2026; date=2026/7 — [record](https://aclanthology.org/2026.findings-acl.163/)

Boundary: Reasoning components qualify when explicitly consumed by counselor generation.

Source SHA-256: `988f497a5599193b26fbbe354339a150d8ac0ce7752b946696cf1b527646b147`



## Schema-Guided Response Generation using Multi-Frame Dialogue State for Motivational Interviewing Systems

`zeng-nakano-2026-schema` · **COUNSELOR / Included** · LLM

Updates structured topic frames, generates MI-grounded dialogue strategies and uses them to generate the next counselor response.

更新多框架对话状态，生成基于 MI 的策略并产生下一轮咨询师回应。

Evidence: §3 Methodology and §3.1 multi-frame dialogue state; PDF p.3 — [reviewed source](https://aclanthology.org/2026.findings-acl.2063.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2026; date=2026/7 — [record](https://aclanthology.org/2026.findings-acl.2063/)

Boundary: Dialogue state tracking qualifies through its direct response-generation pipeline.

Source SHA-256: `8d147c5e2ef05667db3f6db62f767ef9a68ff42b8fc81bd203ca3ec8afa7eb1c`



## TheraMind: A Strategic and Adaptive Agent for Longitudinal Psychological Counseling

`hu2026theramind` · **COUNSELOR / Included** · LLM

TheraMind implements within-session tactical counseling and cross-session strategic planning in a dual-loop counselor agent.

TheraMind 使用会谈内战术执行与跨会谈战略规划的双循环咨询代理。

Evidence: §3 Methodology, dual-loop architecture; author preprint v2 PDF p.3 — [reviewed source](https://arxiv.org/pdf/2510.25758v2)

Publication: ACM WWW 2026 proceedings table of contents, PDF page 114: exact title, starting page 9136, DOI 10.1145/3774904.3793049; proceedings front matter dates April 13-17, 2026. — [record](https://publications.hse.ru/pubs/share/direct/1152301113.pdf)

Boundary: Author preprint v2 reviewed; formal WWW publication verified separately.

Source SHA-256: `eb53f00d39158067850028dd6f9f502be608b943fad96019d714d42f26db5397`



## The Distress Analysis Interview Corpus of Human and Computer Interviews

`gratch2014distress` · **SUPPORT / Supporting** · Historical non-LLM

DAIC describes a corpus of human and automated distress-assessment interviews, with recordings, system logs and questionnaire data. The reported contribution is a screening/interview resource rather than a new supportive-intervention or client-simulation process.

DAIC 主要贡献是困扰评估访谈语料及多模态记录；访谈用于筛查，没有提出新的心理支持干预或来访者模拟过程。

Evidence: §2 Collection and §3 Corpus Composition; PDF pp.2–3 — [reviewed source](https://www.lrec-conf.org/proceedings/lrec2014/pdf/508_Paper.pdf)

Publication: Official LREC 2014 proceedings page lists the exact title, full paper PDF, and BibTeX: Proceedings of the Ninth International Conference on Language Resources and Evaluation, ELRA, May 2014. — [record](https://www.lrec-conf.org/proceedings/lrec2014/summaries/508.html)

Boundary: An automated screening interviewer is not automatically a counseling intervention.

Source SHA-256: `0bd733735e178064fe8a1b52bc50496a19b340b6d272054428812e78f0bdc7bf`



## Anno-MI: A Dataset of Expert-Annotated Counselling Dialogues

`wu2022annomi` · **SUPPORT / Supporting** · Resource / no new role model

AnnoMI professionally transcribes and expert-annotates recorded MI demonstrations, then analyzes behavior distributions and discusses potential applications. The original paper does not implement counselor generation or client simulation.

AnnoMI 转录并标注 MI 演示对话，分析行为分布并讨论应用，没有实现咨询师生成或来访者模拟。

Evidence: §2 Building Counselling Dataset and §3 analyses/potential applications; accepted manuscript PDF pp.2–4 — [reviewed source](https://abdn.elsevierpure.com/ws/portalfiles/portal/213285217/Wu_etal_Anno_Mi_A_AAM.pdf)

Publication: Crossref publisher-deposited record matches title; type=proceedings-article; venue=ICASSP 2022 - 2022 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP); publication date=[2022, 5, 23]; DOI=10.1109/icassp43922.2022.9746035 — [record](https://api.crossref.org/works/10.1109%2FICASSP43922.2022.9746035)

Boundary: Use the ICASSP 2022 paper, not a later dataset extension or follow-up model paper.

Source SHA-256: `636a68fe5c257fcf1b3077f7424f6d9515b26208362e5e2b08e24971d217b31e`



## Consistent Client Simulation for Motivational Interviewing-Based Counseling

`yang-etal-2025-consistent` · **CLIENT / Included** · LLM

Generates client utterances using profile-conditioned state transitions, action selection, information selection and response generation for MI interaction.

通过画像控制的状态转换、行动选择、信息选择与回应生成模拟 MI 来访者。

Evidence: §3 Client Simulation Framework; PDF p.3 — [reviewed source](https://aclanthology.org/2025.acl-long.1021.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2025/7 — [record](https://aclanthology.org/2025.acl-long.1021/)

Boundary: Simulated client planning is not counselor intervention planning.

Source SHA-256: `58b1e76e15d72966e9209769427d78a5f871f0a6de709eaa04e53b98243e0b98`



## From Conversation to Automation: Leveraging LLMs for Problem-Solving Therapy Analysis

`aghakhani-etal-2025-conversation` · **SUPPORT / Supporting** · LLM

Applies LLMs to annotate and analyze already-recorded problem-solving-therapy utterances. Real-time support is a possible future application, not an implemented counselor response policy in the reported method.

用 LLM 标注和分析已有问题解决疗法话语；实时辅助是未来应用，没有实现新的咨询师回应策略。

Evidence: §3 Method, data and coding existing PST therapist utterances; PDF p.3 — [reviewed source](https://aclanthology.org/2025.findings-acl.1292.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2025; date=2025/7 — [record](https://aclanthology.org/2025.findings-acl.1292/)

Boundary: A proposed future use does not satisfy implemented-role eligibility.

Source SHA-256: `5db749fc8173efe22dc156739b5d171f95bd324b250adebeefcfd3024e8d5d46`



## Stress-Testing Emotional Support Models: Moving from Homogeneous to Diverse Help Seekers

`heo-etal-2026-stress` · **CLIENT / Included** · LLM

Trains a next-seeker-utterance model and feature-routed mixture of experts to simulate diverse, profile-controlled psychological and linguistic behaviors during emotional-support interaction.

训练画像控制的求助者话语模型，并通过专家路由控制心理与语言行为多样性。

Evidence: §3.4 profiles and §4 Seeker Simulator Training; PDF p.4 — [reviewed source](https://aclanthology.org/2026.findings-acl.1146.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2026; date=2026/7 — [record](https://aclanthology.org/2026.findings-acl.1146/)

Boundary: A stress-testing paper can qualify through an implemented seeker simulator.

Source SHA-256: `c6383aa0a54fb4e08821d4059bf6e3ed19a59179f84d44b6c8f6f25da34a2be7`



## EmoHarbor: Evaluating Personalized Emotional Support by Simulating the User's Internal World

`ye-etal-2026-emoharbor` · **CLIENT / Included** · LLM

Implements user thinker, talker and evaluator agents; the talker generates the next help-seeker utterance from evolving private cognitive/emotional state and dialogue context.

用户思考、说话和评价代理维护内部状态并生成下一轮求助者话语，属于来访者模拟。

Evidence: §2.2 user thinker/talker and state-update equations; PDF pp.3–4 — [reviewed source](https://aclanthology.org/2026.acl-long.53.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2026/7 — [record](https://aclanthology.org/2026.acl-long.53/)

Boundary: User-as-judge evaluation also contains an explicit interactive user model.

Source SHA-256: `6a900ac6575030cbdb4d901a7f615616a56aa8ffff0a4dd1a7122216d222ffde`



## RECAP: Resistance Capture in Text-based Mental Health Counseling with Large Language Models

`li-etal-2026-recap` · **SUPPORT / Supporting** · LLM

Builds a resistance taxonomy and annotated resource and classifies observed client resistance with explanations. It does not generate a simulated client trajectory or counselor support actions.

构建阻抗分类体系和标注资源，对已发生的来访者行为分类并解释，没有模拟行为或产生咨询行动。

Evidence: §4 ClientResistance construction and §5 RECAP classifier; PDF pp.5–6 — [reviewed source](https://aclanthology.org/2026.conll-main.33.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 30th Conference on Computational Natural Language Learning; date=2026/7 — [record](https://aclanthology.org/2026.conll-main.33/)

Boundary: Classification of client resistance is not generation of client resistance.

Source SHA-256: `99b1169afa6a8aae75e81bc774748c1056887bf67851d02c896f50963d296dea`



## On the Role of Context in LLM Alignment to Mental Health Counseling Competencies

`puspo-etal-2026-role` · **SUPPORT / Supporting** · LLM

Evaluates counselor-competency answers on static exam-derived cases under different context and role prompts. Assigning a counselor persona to an exam answerer does not implement a counseling interaction policy.

使用考试病例与选择题评估咨询知识、上下文和角色提示；扮演咨询师答题不等同建模咨询互动。

Evidence: §3 Methods, CounselingBench and context/prompt ablation; PDF pp.3–5 — [reviewed source](https://aclanthology.org/2026.clpsych-1.6.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 11th Workshop on Computational Linguistics and Clinical Psychology (CLPsych 2026); date=2026/7 — [record](https://aclanthology.org/2026.clpsych-1.6/)

Boundary: Prompted occupational identity alone is insufficient.

Source SHA-256: `41ba1094386adcf1e5b24f88bc7cd21448db11e5fae0344d4e491985941131b6`



## LLMs as Standardised Patients for Motivational Interviewing: How Faithful Are They?

`hoang-etal-2026-llms` · **CLIENT / Included** · LLM

Adapts an MI patient simulation framework using real participant profiles and has simulated patients interact with the same MI coaches to measure faithfulness against human conversations.

基于真实参与者画像适配 MI 病人模拟，并与教练开展对话来验证模拟忠实度。

Evidence: §3.1.2 Simulated Data; PDF p.3 — [reviewed source](https://aclanthology.org/2026.clpsych-1.21.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 11th Workshop on Computational Linguistics and Clinical Psychology (CLPsych 2026); date=2026/7 — [record](https://aclanthology.org/2026.clpsych-1.21/)

Boundary: Explicit MI counseling qualifies even when the behavior topic is physical activity.

Source SHA-256: `ae870c17bb7906c036914a4891d4fe95cc53f3658e8918d470351fe09a206383`



## PsychePass: Calibrating LLM Therapeutic Competence via Trajectory-Anchored Tournaments

`chen-etal-2026-psychepass` · **BOTH / Included** · LLM

Implements script/trajectory-conditioned simulated clients and trains a counselor policy with tournament-derived rewards and trajectory-level reinforcement learning. Both roles qualify despite the evaluation framing.

既实现脚本和轨迹控制的模拟来访者，又用锦标赛奖励进行咨询师策略优化，归双角色。

Evidence: §3.1 script-guided clients and §3.3 trajectory-guided counselor optimization; PDF pp.3–6 — [reviewed source](https://aclanthology.org/2026.findings-acl.1993.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2026; date=2026/7 — [record](https://aclanthology.org/2026.findings-acl.1993/)

Boundary: The saved canonical SFPE target is the evaluation framework; those labels are not a fresh audit of the trained counselor.

Source SHA-256: `9a4e5da2b796013454f02056f24743e9af8068bf8878ef2bb413e003a5ea6389`



## CBT-Bench: Evaluating Large Language Models on Assisting Cognitive Behavior Therapy

`zhang-etal-2025-cbt` · **SUPPORT / Supporting** · LLM

Introduces knowledge, cognitive-classification and deliberate-practice response benchmarks and evaluates existing LLMs. It does not propose a new counselor response policy or interactive client model.

提出知识、认知分类和回应练习基准，评估现成 LLM；没有提出新的咨询师策略或交互来访者模型。

Evidence: §3.1–3.3 benchmark tasks and §4 experiments; PDF pp.3–6 — [reviewed source](https://aclanthology.org/2025.naacl-long.196.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers); date=2025/4 — [record](https://aclanthology.org/2025.naacl-long.196/)

Boundary: Generating responses as benchmark answers does not turn the benchmark into a new role-modeling method.

Source SHA-256: `1d89dae601dc6911be7a45516b19b9890dde8ac4d38a9c2e4a1950d0a2619d7f`



## Measuring What Matters!! Assessing Therapeutic Principles in Mental-Health Conversation

`mazhar-etal-2026-measuring` · **SUPPORT / Supporting** · LLM and pretrained neural classifiers

Annotates therapeutic principles and trains CARE to assign ordinal ratings to observed therapist utterances. Its output is a quality assessment, not a support response or client utterance.

标注治疗原则并训练 CARE 对咨询师话语进行序数评分，输出是质量评估而非支持或来访者回应。

Evidence: §3 FAITH-M and §4 CARE ordinal classifier; PDF pp.4–6 — [reviewed source](https://aclanthology.org/2026.acl-long.731.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2026/7 — [record](https://aclanthology.org/2026.acl-long.731/)

Boundary: Counselor-framed rating explanations are retrospective evaluation.

Source SHA-256: `1eb57ee1079fff3d37e2ec1530912dc05f97b9499601677ef79e79b72c4bcfd5`



## PUPPET: Neural-Symbolic Standardized Patients for Mental Health

`xu-etal-2026-puppet` · **CLIENT / Included** · LLM / neural-symbolic

A neural-symbolic standardized patient updates internal state in response to trainee actions and generates patient utterances through an Observe–Think–Behave loop.

神经符号标准化病人根据训练者行动更新内部状态，并经观察、思考、行为循环生成回应。

Evidence: §3.1 PUPPET-Trainer and §3.3 Observe–Think–Behave; PDF pp.4–5 — [reviewed source](https://aclanthology.org/2026.acl-long.121.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); date=2026/7 — [record](https://aclanthology.org/2026.acl-long.121/)

Boundary: Its causal states belong to the simulated patient, not the counselor.

Source SHA-256: `05f99ed5687c1aa208d247737695f2acbb028b3ebc3bde430f92188cfac335aa`



## MHSafeEval: Role-Aware Interaction-Level Evaluation of Mental Health Safety in Large Language Models

`lee-etal-2026-mhsafeeval` · **CLIENT / Included** · LLM

Implements a history/profile-conditioned client policy and iteratively refines coherent adversarial client trajectories to test counselor safety.

实现以历史和画像为条件的客户端策略，并迭代优化连贯的对抗来访者轨迹，用于咨询安全评估。

Evidence: §4.2 Adversarial Interaction Generation, client-policy equation; PDF p.5 — [reviewed source](https://aclanthology.org/2026.findings-acl.1382.pdf)

Publication: Publisher citation metadata matches title; venue=Findings of the Association for Computational Linguistics: ACL 2026; date=2026/7 — [record](https://aclanthology.org/2026.findings-acl.1382/)

Boundary: Evaluation papers qualify when they implement a dedicated client-generation policy.

Source SHA-256: `2e5e5ccbd27e4b577796eb2a3c8242a6a6555eea9e5ce7b5be89c86686fcb1fe`



## CRADLE Bench: A Clinician-Annotated Benchmark for Multi-Faceted Mental Health Crisis and Safety Risk Detection

`byun-etal-2026-cradle` · **SUPPORT / Supporting** · LLM and pretrained neural classifiers

Constructs clinician-annotated crisis narratives and benchmarks risk-detection labels. It does not generate a counselor support intervention or simulated patient interaction.

构建临床标注的危机叙述并评估风险检测，不生成咨询干预或来访者互动。

Evidence: §3 CRADLE Bench construction and crisis-label schema; PDF pp.2–3 — [reviewed source](https://aclanthology.org/2026.eacl-long.73.pdf)

Publication: Publisher citation metadata matches title; venue=Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers); date=2026/3 — [record](https://aclanthology.org/2026.eacl-long.73/)

Boundary: A safety benchmark without an eligible generative role remains supporting literature.

Source SHA-256: `141c3b26cdc53e3ac56c454586b3a99991ea3c714149d9eca8b55d62512b61c7`



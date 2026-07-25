import os
import json

CATEGORIES = [
    "Artificial Intelligence",
    "Machine Learning",
    "Computer Vision",
    "Natural Language Processing",
    "Robotics",
    "Cyber Security",
    "Cloud Computing"
]

DATASET_SAMPLES = [
    # Artificial Intelligence
    ("Artificial intelligence systems leverage automated reasoning, logic programming, and autonomous agent frameworks to solve multi-modal decision tasks.", "Artificial Intelligence"),
    ("General AI architectures focus on multi-agent collaboration, heuristic search algorithms, and cognitive computing representations.", "Artificial Intelligence"),
    ("Knowledge graph representations and expert systems form core symbolic reasoning engines in enterprise artificial intelligence.", "Artificial Intelligence"),

    # Machine Learning
    ("Gradient boosted decision trees and deep neural networks are trained using supervised loss optimization on high-dimensional feature vectors.", "Machine Learning"),
    ("Supervised learning, unsupervised clustering, and reinforcement learning policy gradients drive modern predictive machine learning pipelines.", "Machine Learning"),
    ("Hyperparameter tuning, cross-validation, and feature scaling ensure generalizable machine learning model generalization.", "Machine Learning"),

    # Computer Vision
    ("Convolutional neural networks, object detection masks, and image segmentation models process pixel arrays and video frame streams.", "Computer Vision"),
    ("Real-time optical flow estimation, facial feature detection, and visual transformer models enable automated camera perception.", "Computer Vision"),
    ("Image classification with ResNet and YOLO bounding box detection algorithms allow spatial computer vision tracking.", "Computer Vision"),

    # Natural Language Processing
    ("Transformer self-attention mechanisms, tokenization, BERT language modeling, and sentiment analysis process unstructured natural text.", "Natural Language Processing"),
    ("Large language models generate coherent textual responses through next-token probability distribution predictions.", "Natural Language Processing"),
    ("Named entity recognition, semantic parsing, and text summarization form fundamental building blocks of NLP.", "Natural Language Processing"),

    # Robotics
    ("Kinematic motion planning, joint torque feedback actuators, and autonomous robot navigation controllers maintain balance.", "Robotics"),
    ("SLAM simultaneous localization and mapping algorithms allow mobile autonomous robots to map physical obstacles.", "Robotics"),
    ("Robotic arm manipulators execute precise trajectory planning and force-sensitive object gripping in industrial automation.", "Robotics"),

    # Cyber Security
    ("Zero-trust network architecture, end-to-end encryption key exchange, intrusion detection systems, and threat vulnerability prevention.", "Cyber Security"),
    ("Penetration testing, cryptographic security protocols, firewall packet filtering, and ransomware mitigation safeguard data.", "Cyber Security"),
    ("Malware behavioral analysis, security operations center monitoring, and identity access management mitigate cyber security risks.", "Cyber Security"),

    # Cloud Computing
    ("Microservice container orchestration with Kubernetes, serverless AWS Lambda functions, and distributed cloud computing infrastructure.", "Cloud Computing"),
    ("Elastic load balancing, cloud storage bucket replication, and infrastructure-as-code automation streamline cloud DevOps.", "Cloud Computing"),
    ("Multi-tenant cloud architectures ensure high availability, auto-scaling, and fault tolerant database deployment across regions.", "Cloud Computing")
]

def prepare_dataset():
    """Generates synthetic dataset items to ensure robust model training."""
    texts = []
    labels = []
    
    # Expand dataset samples with domain variation patterns
    for text, category in DATASET_SAMPLES:
        texts.append(text)
        labels.append(category)
        # Augment with slight variations
        texts.append(f"Research paper on {category}: {text}")
        labels.append(category)
        texts.append(f"Technical report regarding {text.lower()}")
        labels.append(category)

    return texts, labels

if __name__ == "__main__":
    t, l = prepare_dataset()
    print(f"Prepared {len(t)} sample instances across {len(set(l))} categories.")

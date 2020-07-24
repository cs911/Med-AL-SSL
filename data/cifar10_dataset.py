import torchvision
from sklearn.model_selection import train_test_split
import numpy as np
from torchvision import transforms
from .dataset_utils import WeaklySupervisedDataset


class Cifar10Dataset:
    def __init__(self, root, labeled_ratio, add_labeled_ratio):
        self.root = root
        self.labeled_ratio = labeled_ratio
        self.cifar_mean = (0.4914, 0.4822, 0.4465)
        self.cifar_std = (0.2023, 0.1994, 0.2010)
        self.input_size = 32
        self.transform_train = transforms.Compose([
            transforms.RandomCrop(self.input_size, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.RandomAffine(degrees=0, translate=(0.125, 0.125)),
            # transforms.RandomVerticalFlip(),
            # transforms.RandomGrayscale(),
            # transforms.RandomRotation(degrees=180),
            # transforms.ColorJitter(brightness=(0.1, 1.5), contrast=(0.75, 1.5), saturation=(0.5, 1.5)),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.cifar_mean, std=self.cifar_std)
        ])
        self.transform_test = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=self.cifar_mean, std=self.cifar_std)
        ])
        self.transform_base = transforms.Compose([
            transforms.ToTensor(),
         ])
        self.num_classes = 10
        self.add_labeled_ratio = add_labeled_ratio
        self.add_labeled_num = None
        self.remove_classes = np.array([0, 1, 2])

    def get_dataset(self):
        base_dataset = torchvision.datasets.CIFAR10(root=self.root, train=True,
                                                    download=True, transform=None)

        self.add_labeled_num = int(len(base_dataset) * self.add_labeled_ratio)

        labeled_indices, unlabeled_indices = train_test_split(
            np.arange(len(base_dataset)),
            test_size=(1 - self.labeled_ratio),
            shuffle=True,
            stratify=None)

        test_dataset = torchvision.datasets.CIFAR10(root=self.root, train=False,
                                                    download=True, transform=self.transform_test)

        targets = np.array(base_dataset.targets)[labeled_indices]
        labeled_indices = labeled_indices[~np.isin(targets, self.remove_classes)]

        labeled_dataset = WeaklySupervisedDataset(base_dataset, labeled_indices, transform=self.transform_train)
        unlabeled_dataset = WeaklySupervisedDataset(base_dataset, unlabeled_indices, transform=self.transform_test)

        return labeled_dataset, unlabeled_dataset, labeled_indices, unlabeled_indices, test_dataset

    def get_base_dataset(self):
        base_dataset = torchvision.datasets.CIFAR10(root=self.root, train=True,
                                                    download=True, transform=self.transform_base)

        return base_dataset

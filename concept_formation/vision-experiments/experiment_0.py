import torch

from concept_formation.cobweb_torch import CobwebTorchTree
from datasets_mnist import dataloaders_0
import models_nn
import models_cobweb


def reconfig(general_config, model_config, data_config):
	"""
	Re-initialization for model_config and data_config based on requirements of experiments 0.
	"""
	if data_config['dataset'] == 'mnist':
		data_config['split_size'] = 6000
	else:
		data_config['split_size'] = 5000
	if model_config['type'] == 'cobweb':
		general_config['cuda'] == False
		data_config['batch_size_tr'] = 60000
		data_config['batch_size_te'] = 10000


def experiment_0_nn(general_config, model_config, data_config, dataset_tr, dataset_te, verbose):

	reconfig(general_config, model_config, data_config)

	# if data_config['dataset'] == 'mnist':
	# 	from datasets_mnist import dataloaders_0
	# else:
	# 	from datasets_cifar import dataloaders_0

	# Dataloaders:
	dataloaders = dataloaders_0(general_config, data_config, dataset_tr, dataset_te, verbose)
	loaders_tr = dataloaders.training_loaders
	loaders_te = dataloaders.test_loaders

	# Models and optimizers:
	device = torch.device("cuda" if general_config['cuda'] else "cpu")
	model, optimizer = models_nn.build_model(model_config, data_config, device)

	# Store the test accuracies
	test_accs = []

	if verbose:
		print('\n\n' + ' START EXPERIMENTS '.center(70, '~'))
		print("Experiments type: 0")
		print("Experiments description: Train data from all labels with sequential splits.")
		print("Number of Train-test trials:", len(loaders_tr))
		print("Model:", model_config['type'])  # fc or cnn
		print("Seed:", general_config['seed'])
		print("Epochs:", model_config['epoch'])
		print("\nModel overview:")
		print(model)
		print("\nOptimizer:")
		print(optimizer)
		print("\nCUDA is {}used.".format("" if general_config['cuda'] else "NOT "))

	for i in range(len(loaders_tr)):
		if verbose:
			print("\n\n" + " Trial {} ".format(i+1).center(70, '='))
		
		for epoch in range(1, model_config['epoch'] + 1):
			if verbose:
				print("\n\n [Epoch {}]".format(epoch))
				print("\n====> Model Training with labels {} <====".format(dataloaders.labels_tr[i]))
			models_nn.train(model, optimizer, loaders_tr[i], epoch, model_config['log_interval'], device)
			
		for j in range(len(loaders_te)):
			if verbose:
				print("\n----> Model Testing with labels {} <----".format(dataloaders.labels_te[j]))
			acc = models_nn.test(model, loaders_te[j], device)
			test_accs.append(acc.item())

	print("\n\nThis is the end of the experiments.")
	print("There are {} test accuracy data in total.".format(len(test_accs)))
	return test_accs


def experiment_0_cobweb(general_config, model_config, data_config, dataset_tr, dataset_te, verbose):

	reconfig(general_config, model_config, data_config)

	# Dataloaders:
	dataloaders = dataloaders_0(general_config, data_config, dataset_tr, dataset_te, verbose)
	loaders_tr = dataloaders.training_loaders
	loaders_te = dataloaders.test_loaders

	# Models and optimizers:
	example_imgs, _ = next(iter(loaders_tr[0]))
	model = CobwebTorchTree(example_imgs.shape[1:])

	# Store the test accuracies
	test_accs = []

	if verbose:
		print('\n\n' + ' START EXPERIMENTS '.center(70, '~'))
		print("Experiments type: 0")
		print("Experiments description: Train data from all labels with sequential splits.")
		print("Number of Train-test trials:", len(loaders_tr))
		print("Model:", model_config['type'])  # cobweb
		print("Seed:", general_config['seed'])
		print("\nCUDA is {}used.".format("" if general_config['cuda'] else "NOT "))

	for i in range(len(loaders_tr)):
		if verbose:
			print("\n\n" + " Trial {} ".format(i+1).center(70, '='))
			print("\n====> Model Training with labels {} <====".format(dataloaders.labels_tr[i]))
		models_cobweb.train(model, loaders_tr[i])
		
		for j in range(len(loaders_te)):
			if verbose:
				print("\n----> Model Testing with labels {} <----".format(dataloaders.labels_te[j]))
			acc = models_cobweb.test(model, loaders_te[j])
			print("Test accuracy: {}".format(acc))
			test_accs.append(acc)

	print("\n\nThis is the end of the experiments.")
	print("There are {} test accuracy data in total.".format(len(test_accs)))
	return test_accs


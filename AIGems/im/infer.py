import torch
import torch.nn as nn
import torch.nn.functional as F
import flask
import torchvision.transforms as transforms
from PIL import Image
import numpy as np


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


net = Net()
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# net.to(device)
PATH = './cifar_net.pth'

net.load_state_dict(torch.load(PATH))
classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

app = flask.Flask(__name__)

@app.route("/", methods=["POST"])
def inf():
    i = Image.open(flask.request.files['img'].stream)
    ip = transform(i)
    ipt = torch.tensor(np.array([ip.numpy()]))
    # ipt.to(device)
    out = net(ipt)
    _, predicted = torch.max(out, 1)
    return f"img content is: {classes[predicted[0]]}"

if __name__ == "__main__":
    app.run()
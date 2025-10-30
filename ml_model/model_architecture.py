#create the architecture of a neural network
import torch.nn as nn

class SentiNN(nn.Module):
    def __init__(self, input_size, embed_size, hidden_size):
        super().__init__()
        self.e=nn.Embedding(input_size, embed_size)
        self.dropout=nn.Dropout(0.2)
        self.rnn=nn.GRU(embed_size,hidden_size, batch_first=True)
        self.out=nn.Linear(in_features=hidden_size,out_features=2)
    
    def forward(self,x):
        x=self.e(x)
        x=self.dropout(x)
        outputs, hidden=self.rnn(x) # hidden is 1 x batch_size x hidden_size
        hidden.squeeze_(0) #now, batch_size x hidden_size 
        logits=self.out(hidden)
        return logits
    
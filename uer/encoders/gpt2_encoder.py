# -*- encoding:utf-8 -*-
import torch
import torch.nn as nn
from uer.layers.layer_norm import LayerNorm
from uer.layers.position_ffn import PositionwiseFeedForward
from uer.layers.multi_headed_attn import MultiHeadedAttention
from uer.layers.transformer import GptBlock

class Gpt2Encoder(nn.Module):
    """
    GPT2 encoder exploits 12 or 24 gptblock layers to extract features.
    """
    def __init__(self, args):
        super(Gpt2Encoder, self).__init__()
        self.layers_num = args.layers_num
        self.block = nn.ModuleList([
            GptBlock(args) for _ in range(self.layers_num)
        ])
        self.layer_norm = LayerNorm(args.hidden_size)
        
    def forward(self, emb, seg):
        """
        Args:
            emb: [batch_size x seq_length x emb_size]
            seg: [batch_size x seq_length]

        Returns:
            hidden: [batch_size x seq_length x hidden_size]
        """

        batch_size, seq_length, _ = emb.size()
        # Generate mask according to segment indicators.
        # mask: [batch_size x 1 x seq_length x seq_length]
        mask = torch.ones(seq_length, seq_length, device=emb.device)
        mask = torch.tril(mask)
        mask = (1.0 - mask) * -10000
        mask = mask.repeat(batch_size, 1, 1, 1)

        hidden = emb
        for i in range(self.layers_num):
            hidden = self.block[i](hidden, mask)
        return self.layer_norm(hidden)
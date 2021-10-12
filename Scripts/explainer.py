import inspect
import re
from abc import ABC, abstractmethod, abstractproperty
from typing import List, Tuple, Union

import torch
from transformers import PreTrainedModel, PreTrainedTokenizer


class BaseExplainer(ABC):
    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer,
    ):
        self.model = model
        self.tokenizer = tokenizer

        if self.model.config.model_type == "gpt2":
            self.ref_token_id = self.tokenizer.eos_token_id
        else:
            self.ref_token_id = self.tokenizer.pad_token_id

        self.sep_token_id = (
            self.tokenizer.sep_token_id
            if self.tokenizer.sep_token_id is not None
            else self.tokenizer.eos_token_id
        )
        self.cls_token_id = (
            self.tokenizer.cls_token_id
            if self.tokenizer.cls_token_id is not None
            else self.tokenizer.bos_token_id
        )

        self.model_prefix = model.base_model_prefix

        if self._model_forward_signature_accepts_parameter("position_ids"):
            self.accepts_position_ids = True
        else:
            self.accepts_position_ids = False

        if self._model_forward_signature_accepts_parameter("token_type_ids"):
            self.accepts_token_type_ids = True
        else:
            self.accepts_token_type_ids = False

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.word_embeddings = self.model.get_input_embeddings()
        self.position_embeddings = None
        self.token_type_embeddings = None

        self._set_available_embedding_types()

    @abstractmethod
    def encode(self, text: str = None):
        """
        Encode given text with a model's tokenizer.
        """
        raise NotImplementedError

    @abstractmethod
    def decode(self, input_ids: torch.Tensor) -> List[str]:
        """
        Decode received input_ids into a list of word tokens.


        Args:
            input_ids (torch.Tensor): Input ids representing
            word tokens for a sentence/document.

        """
        raise NotImplementedError

    @abstractproperty
    def word_attributions(self):
        raise NotImplementedError

    @abstractmethod
    def _run(self) -> list:
        raise NotImplementedError

    @abstractmethod
    def _forward(self):
        """
        Forward defines a function for passing inputs
        through a models's forward method.

        """
        raise NotImplementedError

    @abstractmethod
    def _calculate_attributions(self):
        """
        Internal method for calculating the attribution
        values for the input text.

        """
        raise NotImplementedError

    def _make_input_reference_pair(
        self, text: Union[List, str]
    ) -> Tuple[torch.Tensor, torch.Tensor, int]:
        """
        Tokenizes `text` to numerical token id  representation `input_ids`,
        as well as creating another reference tensor `ref_input_ids` of the same length
        that will be used as baseline for attributions. Additionally
        the length of text without special tokens appended is prepended is also
        returned.

        Args:
            text (str): Text for which we are creating both input ids
            and their corresponding reference ids

        Returns:
            Tuple[torch.Tensor, torch.Tensor, int]
        """

        if isinstance(text, list):
            raise NotImplementedError("Lists of text are not currently supported.")
        tt = text.split(" ")
        div_num = int(len(tt)/510)
        print(div_num)
        input_ids = []
        ref_input_ids = [self.ref_token_id]*2048
        for x in range(0,4):
            if(x!=3 and x!=div_num):
                current_text = tt[x*510:(x*510)+510]
           #     print("len of current-text: " + str(len(current_text)))
                current_text = ' '.join(current_text)
          #      print(current_text)
                enc_text = self.encode(current_text)
                ref_input_ids[x*512] = self.cls_token_id
                ref_input_ids[x*512+511] = self.sep_token_id
            else:
                current_text = tt[x*510:min(len(tt), x*510+510)]
                current_text = ' '.join(current_text)
                enc_text = self.encode(current_text)
                ref_input_ids[x*512] = self.cls_token_id
               # ref_input_ids[x*512+511] = self.sep_token_id
            input_ids.extend(enc_text)
        if(len(input_ids) < 2048):
            input_ids = input_ids[:-1]
            while(len(input_ids) < 2048):
                input_ids.append(0)
        else:
            ref_input_ids[2047] = self.sep_token_id
       # text_ids = self.encode(text)
       # text_ids = text_ids[1:-1]
        #input_ids = self.tokenizer.encode(text, add_special_tokens=True)
      #  input_ids = [0]*2048
        print(len(input_ids))
        print("ref id length is: " + str(len(ref_input_ids)))
       # ref_input_ids = [self.ref_token_id]*2048
      #  j = 0
      #  flag = True
      #  while j < 4 and flag == True:
     #       z = j*512
      #      print(z)
      #      input_ids[z] = self.cls_token_id
      #      ref_input_ids[z] = self.cls_token_id
      #      if(z+510 > len(text_ids)):
      #          leftover = len(text_ids) - j*510 + 1
      #          input_ids[z+1:z+leftover] = text_ids[j*510:len(text_ids)]
      #      else:
       #         input_ids[z+1:z+511] = text_ids[j*510:j*510+510]
           # input_ids[z+1:min(z+511, len(text_ids))] = text_ids[j*510:min(j*510+510, len(text_ids))]
       #     if(len(text_ids) < j*510+510):
        #        flag = False
        #    else:
         #       input_ids[z+511] = self.sep_token_id
         #       ref_input_ids[z+511] = self.sep_token_id
         #   j = j + 1
    #    print(len(input_ids))
  #      print(input_idasdasdas)
        # if no special tokens were added

        #FIX THIS TO BE CLS TOKENS IN THE CORRECT SPOT ETC>

       # if len(text_ids) == len(input_ids):
       #     ref_input_ids = [self.ref_token_id] * len(text_ids)
       # else:
       #     ref_input_ids = (
       #         [self.cls_token_id]
        #        + [self.ref_token_id] * len(text_ids)
         #       + [self.sep_token_id]
          #  )

        return (
            torch.tensor([input_ids], device=self.device),
            torch.tensor([ref_input_ids], device=self.device),
            len(input_ids),
        )

    def _make_input_reference_token_type_pair(
        self, input_ids: torch.Tensor, sep_idx: int = 0
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns two tensors indicating the corresponding token types for the `input_ids`
        and a corresponding all zero reference token type tensor.
        Args:
            input_ids (torch.Tensor): Tensor of text converted to `input_ids`
            sep_idx (int, optional):  Defaults to 0.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]
        """
        seq_len = input_ids.size(1)
        token_type_ids = torch.tensor(
            [0 if i <= sep_idx else 1 for i in range(seq_len)], device=self.device
        ).expand_as(input_ids)
        ref_token_type_ids = torch.zeros_like(
            token_type_ids, device=self.device
        ).expand_as(input_ids)

        return (token_type_ids, ref_token_type_ids)

    def _make_input_reference_position_id_pair(
        self, input_ids: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns tensors for positional encoding of tokens for input_ids and zeroed tensor for reference ids.

        Args:
            input_ids (torch.Tensor): inputs to create positional encoding.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]
        """
        seq_len = input_ids.size(1)
        position_ids = torch.arange(seq_len, dtype=torch.long, device=self.device)
        ref_position_ids = torch.zeros(seq_len, dtype=torch.long, device=self.device)
        position_ids = position_ids.unsqueeze(0).expand_as(input_ids)
        ref_position_ids = ref_position_ids.unsqueeze(0).expand_as(input_ids)
        return (position_ids, ref_position_ids)

    def _make_attention_mask(self, input_ids: torch.Tensor) -> torch.Tensor:
        am = []
        for x in input_ids[0]:
            if(x == 0):
                am.append(0)
            else:
                am.append(1)
       # print(am)
       # print(len(am))
        return torch.Tensor(am)

    def _clean_text(self, text: str) -> str:
        text = re.sub("([.,!?()])", r" \1 ", text)
        text = re.sub("\s{2,}", " ", text)
        return text

    def _model_forward_signature_accepts_parameter(self, parameter: str) -> bool:
        signature = inspect.signature(self.model.forward)
        parameters = signature.parameters
        return parameter in parameters

    def _set_available_embedding_types(self):
        model_base = getattr(self.model, self.model_prefix)
        if self.model.config.model_type == "gpt2" and hasattr(model_base, "wpe"):
            self.position_embeddings = model_base.wpe.weight
        else:
            if hasattr(model_base, "embeddings"):
                self.model_embeddings = getattr(model_base, "embeddings")
                if hasattr(self.model_embeddings, "position_embeddings"):
                    self.position_embeddings = self.model_embeddings.position_embeddings
                if hasattr(self.model_embeddings, "token_type_embeddings"):
                    self.token_type_embeddings = (
                        self.model_embeddings.token_type_embeddings
                    )

    def __str__(self):
        s = f"{self.__class__.__name__}("
        s += f"\n\tmodel={self.model.__class__.__name__},"
        s += f"\n\ttokenizer={self.tokenizer.__class__.__name__}"
        s += ")"

        return s

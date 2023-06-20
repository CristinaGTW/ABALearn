# Learning Logic-Based Argumentation

## Prerequisites

* Python 3.10 
* pyswip 
* SWI-Prolog 7.2.x or higher

## To run:
```
python abalearn.py <input_file_path>
```
## Input file format:
* ### Prolog file:
    See `small_examples\` for examples. \
    Specify an ABA learning problem with ground facts as follows:\
    __Background Knowledge:__
    * *Rule:*  `my_rule(RuleId,Head,Body).` 
    > Example: `my_rule(r1, siblings(X,Y),[mom(A,X), mom(B,Y), A=B]).`
    * *Assumption:*  `my_asm(Asm).` 
    > Example: `my_asm(alpha1(X)).`
    * *Contrary mapping:*  `contrary(Asm,CAsm).` 
    > Example: `contrary(alpha1(X),c_alpha1(X)).`
    __Training Data:__
    * *Positive example:* `pos(ExId, Ex).`
    > Example: `pos(p1,flies(a)).`
    * *Negative example:* `neg(ExId, Ex).`
    > Example: `neg(n1,flies(c)).`
        
* ### Tabular data (CSV file):
    See `datasets\` for examples. \
    Requirements:
    * Must only contain discrete values
    * First column must contain record identifiers
    * Last column must contain labelling indicated by positive/negative values only (e.g., true/false, yes/no)
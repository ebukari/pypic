# pypic
compare pypi packages

still in beta

## Install
`pip install pypic`

## Usage
### as python module
```python
import pypic as pp
```

**Normalise a package name**
```python
>>>pp.normalise("me--test")
'me-test'
>>>pp.normalsie("me.test")
'me-test'
```

**Check if a package exists on pypi**
```python
>>>pp.check("pypic")
True
#Checking if a particular version exists
>>>pp.check("pypic", version="0.1.0")
True
```

### Contributing
```python
while True:
    git.fork(project)

    if project.new_feature or project.fixed_bug:
        git.send_pull_request(project)

```

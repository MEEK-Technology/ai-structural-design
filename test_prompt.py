# from nlp.prompt_parser import extract_parameters, apply_defaults

# prompt = "Design a beam with span 6m and load 25kN/m with grade 30 concrete and 500 MPa steel"

# params = extract_parameters(prompt)
# params = apply_defaults(params)

# print(params)

from nlp.prompt_parser import extract_parameters, apply_defaults

# prompt = "Design a beam with span 6m and load 25kN/m with 25 fck concrete and 800 MPa steel"
# prompt = "Design a beam with span 17m and load 40kN/m with fcu 30 concrete and 750 MPa steel"
prompt = "Design a beam with span 17m and load 40kN/m with fck 35 concrete and fy 660 steel"
# prompt = "Design a beam with span 17m and load 40kN/m with concrete grade 35 and steel grade 500"
# prompt = "Design a beam with span 17m and load 40kN/m with grade of concrete 55 and grade of steel 580"


params = extract_parameters(prompt)
params = apply_defaults(params)

print(params)
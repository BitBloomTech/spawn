from os import path
folder = path.dirname(path.realpath(__file__))
turbsim_exe = path.join(folder, 'TurbSim.exe')
fast_exe = path.join(folder, 'FASTv7.0.2.exe')
turbsim_input_file = path.join(folder, 'fast_input_files', 'TurbSim.inp')
fast_input_file = path.join(folder, 'fast_input_files', 'NRELOffshrBsline5MW_Onshore.fst')
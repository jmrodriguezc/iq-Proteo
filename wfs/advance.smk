# include the main functions and the global variables
include: "inc/main.smk"

# include the rules for the pRatio section
include: "inc/pratio.smk"

# include the rules for the pRatio section
include: "inc/sanxot.adv.smk"

# include the rules for the pRatio section
include: "inc/compilator.smk"

# default target rule
rule all:
    '''
    Config the output files
    '''
    input:
        infiles_adv( INFILE_DAT )

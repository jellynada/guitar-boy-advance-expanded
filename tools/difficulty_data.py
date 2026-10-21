"""Runtime difficulty metadata and bounded menu-chart header generation."""
import copy
try:
    from .adapt_chart import header
except ImportError:
    from adapt_chart import header
LAYOUTS={'Easy':['LEFT','B','A'], 'Medium':['LEFT','RIGHT','B','A'], 'Hard':['LEFT','UP/DOWN','RIGHT','B','A']}

def bundle_header(charts):
    largest=max(range(len(charts)),key=lambda i:charts[i]['note_count'])
    # Keep imported_notes as a real max-capacity array for ROM/ELF verification.
    result=[];choices=[]
    for i,chart in enumerate(charts):
        data=copy.deepcopy(chart);data['difficulty']='Easy'
        text=header(data)
        names={'imported_notes':'imported_notes' if i==largest else f'chart_notes_{i}',
               'imported_sustain_us':'imported_sustain_us' if i==largest else f'chart_holds_{i}'}
        if i!=largest:
            for token in ['imported_note_count','imported_is_synthetic','imported_title','imported_ticks_per_frame','imported_pre_roll_us']:
                text=text.replace(token,f'chart_{i}_'+token.removeprefix('imported_'))
        for token,value in names.items():text=text.replace(token,value)
        result.append(text)
        choices.append('{'+names['imported_notes']+','+names['imported_sustain_us']+','+str(chart['note_count'])+','+str(len(LAYOUTS[chart['difficulty']]))+',"'+chart['difficulty']+'"}')
    result+=['#define GBA_IMPORTED_CHOICES 1','#include "importedChoice.hpp"',
             'inline constexpr ImportedChartChoice imported_choices[]={'+','.join(choices)+'};']
    return '\n'.join(result)+'\n'

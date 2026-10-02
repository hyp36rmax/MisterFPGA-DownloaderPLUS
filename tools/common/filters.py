"""Default-filter validation for explicitly selected hardware inventories."""
import copy
import re

from tools.common.file_types import is_mra
from tools.common.database import ValidationError
from tools.common.archives import expanded_inventory


def normalized_term(term):
    return term.lower().replace('-', '').replace('_', '')


def parse_filter(value, dictionary):
    # Standard installation has an empty global filter. User overrides stay user-owned.
    value=value.lower().replace('[mister]', '').strip()
    if value in ('','all'):return [],[],False
    if value=='!all':return [],[],True
    positive=[];negative=[];positive_all=False
    for part in value.split():
        if not re.fullmatch(r'!?[a-z0-9]+[-_a-z0-9.]*',part):
            raise ValidationError('DERIVED FILTER CONFLICT: unsupported filter syntax')
        excluded=part.startswith('!');term=normalized_term(part.lstrip('!'))
        if term=='none' or (term=='all' and excluded):
            raise ValidationError('DERIVED FILTER CONFLICT: unsupported filter term')
        if term=='all':positive_all=True;continue
        (negative if excluded else positive).append(dictionary.get(term,term))
    essential=dictionary.get('essential','essential')
    if positive and essential not in positive and essential not in negative:positive.append(essential)
    return [] if positive_all else positive,negative,False


def installable(record, parsed):
    positive,negative,never=parsed;tags=record.get('tags',[])
    return not never and (not positive or bool(set(positive)&set(tags))) and not (set(negative)&set(tags))


def filter_counts(database, value=None):
    inventory=expanded_inventory(database)
    value=database.get('default_options',{}).get('filter','') if value is None else value
    parsed=parse_filter(value,database.get('tag_dictionary',{}))
    primary={p:r for p,r in inventory['files'].items() if is_mra(p) and '_alternatives' not in p.split('/')}
    alternatives={p:r for p,r in inventory['files'].items() if is_mra(p) and '_alternatives' in p.split('/')}
    installed=sum(installable(r,parsed) for r in primary.values())
    alt_installed=sum(installable(r,parsed) for r in alternatives.values())
    return {'selected_primary_mras':len(primary),'default_installable_primary_mras':installed,
            'filtered_primary_mras':len(primary)-installed,'selected_alternative_mras':len(alternatives),
            'default_installable_alternative_mras':alt_installed,'filtered_alternative_mras':len(alternatives)-alt_installed,
            'filtered_selected_files':sum(not installable(r,parsed) for r in inventory['files'].values()),
            'filtered_selected_folders':sum(not installable(r,parsed) for r in inventory['folders'].values())}


def validate_filter_policy(policy):
    if type(policy) is not dict or not {'inventory','remove_conflicting_exclusions'} <= set(policy) <= {'inventory','remove_conflicting_exclusions','reason'}:
        raise ValidationError('Invalid derived filter policy')
    if not isinstance(policy['inventory'],str) or policy['inventory'] not in {'complete','intentional-subset'} or type(policy['remove_conflicting_exclusions']) is not bool:
        raise ValidationError('Invalid derived filter policy')
    if policy['inventory']=='intentional-subset' and (policy['remove_conflicting_exclusions'] or not isinstance(policy.get('reason'),str) or not policy['reason'].strip()):
        raise ValidationError('Intentional filter subset requires a documented reason and preservation')
    if 'reason' in policy and (not isinstance(policy['reason'],str) or not policy['reason'].strip()):
        raise ValidationError('Invalid derived filter policy reason')


def derived_default_options(database, config):
    options=copy.deepcopy(database.get('default_options'))
    if config.get('source_mode') not in {'database','repository'}:return options
    policy=config.get('filter_policy',{'inventory':'complete','remove_conflicting_exclusions':False})
    validate_filter_policy(policy)
    value=(options or {}).get('filter','')
    counts=filter_counts(database,value)
    conflict=counts['filtered_selected_files'] or counts['filtered_selected_folders']
    if policy['inventory']=='intentional-subset':
        if counts['selected_primary_mras'] and not counts['default_installable_primary_mras']:
            raise ValidationError('DERIVED FILTER CONFLICT: intentional subset is empty')
        return options
    if not conflict:return options
    if not policy['remove_conflicting_exclusions']:
        raise ValidationError('DERIVED FILTER CONFLICT: default suppresses selected inventory')
    dictionary=database.get('tag_dictionary',{});inventory=expanded_inventory(database)
    records=list(inventory['files'].values())+list(inventory['folders'].values())
    terms=[]
    for part in value.split():
        term=normalized_term(part[1:]) if part.startswith('!') else ''
        # Only ordinary, known excluded tags affecting selected records are approved.
        conflicting=part.startswith('!') and term in dictionary and any(dictionary[term] in r.get('tags',[]) for r in records)
        if not conflicting:terms.append(part)
    corrected=' '.join(terms)
    after=filter_counts(database,corrected)
    if after['filtered_selected_files'] or after['filtered_selected_folders']:
        raise ValidationError('DERIVED FILTER CONFLICT: approved exclusions cannot resolve default')
    options['filter']=corrected
    return options

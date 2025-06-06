﻿"""Creates models used by the test suite."""

import mph
from jpype import JInt
from jpype import JBoolean


def capacitor():
    """Creates the tutorial model."""
    model = mph.session.client.create('capacitor')

    parameters = model/'parameters'
    (parameters/'Parameters 1').rename('parameters')
    model.parameter('U', '1[V]')
    model.description('U', 'applied voltage')
    model.parameter('d', '2[mm]')
    model.description('d', 'electrode spacing')
    model.parameter('l', '10[mm]')
    model.description('l', 'plate length')
    model.parameter('w', '2[mm]')
    model.description('w', 'plate width')

    functions = model/'functions'
    step = functions.create('Step', name='step')
    step.property('funcname', 'step')
    step.property('location', -0.01)
    step.property('smooth', 0.01)

    components = model/'components'
    components.create(True, name='component')

    geometries = model/'geometries'
    geometry = geometries.create(2, name='geometry')
    anode = geometry.create('Rectangle', name='anode')
    anode.property('pos', ['-d/2-w/2', '0'])
    anode.property('base', 'center')
    anode.property('size', ['w', 'l'])
    cathode = geometry.create('Rectangle', name='cathode')
    cathode.property('base', 'center')
    cathode.property('pos',  ['+d/2+w/2', '0'])
    cathode.property('size', ['w', 'l'])
    vertices = geometry.create('BoxSelection', name='vertices')
    vertices.property('entitydim', 0)
    rounded = geometry.create('Fillet', name='rounded')
    rounded.property('radius', '1[mm]')
    rounded.java.selection('point').named(vertices.tag())
    medium1 = geometry.create('Rectangle', name='medium 1')
    medium1.property('pos',  ['-max(l,d+2*w)', '-max(l,d+2*w)'])
    medium1.property('size', ['max(l,d+2*w)', 'max(l,d+2*w)*2'])
    medium2 = geometry.create('Rectangle', name='medium 2')
    medium2.property('pos',  ['0', '-max(l,d+2*w)'])
    medium2.property('size', ['max(l,d+2*w)', 'max(l,d+2*w)*2'])
    axis = geometry.create('Polygon', name='axis')
    axis.property('type', 'open')
    axis.property('source', 'table')
    axis.property('table', [
        ['-d/2', '0'],
        ['-d/4', '0'],
        ['0',    '0'],
        ['+d/4', '0'],
        ['+d/2', '0'],
    ])
    model.build(geometry)

    coordinates = model/'coordinates'
    (coordinates/'Boundary System 1').rename('boundary system')

    views = model/'views'
    view = views/'View 1'
    view.rename('view')
    view.java.axis().label('axis')
    view.java.axis().set('xmin', -0.01495)
    view.java.axis().set('xmax', +0.01495)
    view.java.axis().set('ymin', -0.01045)
    view.java.axis().set('ymax', +0.01045)

    selections = model/'selections'
    anode_volume = selections.create('Disk', name='anode volume')
    anode_volume.property('posx', '-d/2-w/2')
    anode_volume.property('r', 'w/10')
    anode_surface = selections.create('Adjacent', name='anode surface')
    anode_surface.property('input', [anode_volume])
    cathode_volume = selections.create('Disk', name='cathode volume')
    cathode_volume.property('posx', '+d/2+w/2')
    cathode_volume.property('r', 'w/10')
    cathode_surface = selections.create('Adjacent', name='cathode surface')
    cathode_surface.property('input', [cathode_volume])
    medium1 = selections.create('Disk', name='medium 1')
    medium1.property('posx', '-2*d/10')
    medium1.property('r', 'd/10')
    medium2 = selections.create('Disk', name='medium 2')
    medium2.property('posx', '+2*d/10')
    medium2.property('r', 'd/10')
    media = selections.create('Union', name='media')
    media.property('input', [medium1, medium2])
    domains = selections.create('Explicit', name='domains')
    domains.select('all')
    exterior = selections.create('Adjacent', name='exterior')
    exterior.property('input', [domains])
    axis = selections.create('Box', name='axis')
    axis.property('entitydim', 1)
    axis.property('xmin', '-d/2-w/10')
    axis.property('xmax', '+d/2+w/10')
    axis.property('ymin', '-l/20')
    axis.property('ymax', '+l/20')
    axis.property('condition', 'inside')
    center = selections.create('Disk', name='center')
    center.property('entitydim', 0)
    center.property('r', 'd/10')
    probe1 = selections.create('Disk', name='probe 1')
    probe1.property('entitydim', 0)
    probe1.property('posx', '-d/4')
    probe1.property('r', 'd/10')
    probe2 = selections.create('Disk', name='probe 2')
    probe2.property('entitydim', 0)
    probe2.property('posx', '+d/4')
    probe2.property('r', 'd/10')

    physics = model/'physics'
    es = physics.create('Electrostatics', geometry, name='electrostatic')
    es.java.field('electricpotential').field('V_es')
    es.select(media)
    es.java.prop('d').set('d', 'l')
    if model.version() >= '6.3':
        (es/'Free Space 1').rename('free space')
        es.create('ChargeConservationSolid', 2, name='Laplace equation')
        (es/'Laplace equation').select(media)
    else:
        (es/'Charge Conservation 1').rename('Laplace equation')
    (es/'Zero Charge 1').rename('zero charge')
    (es/'Initial Values 1').rename('initial values')
    anode = es.create('ElectricPotential', 1, name='anode')
    anode.select(anode_surface)
    anode.property('V0', '+U/2')
    cathode = es.create('ElectricPotential', 1, name='cathode')
    cathode.select(cathode_surface)
    cathode.property('V0', '-U/2')
    ec = physics.create('ConductiveMedia', geometry, name='electric currents')
    ec.java.field('electricpotential').field('V_ec')
    ec.select(media)
    ec.java.prop('d').set('d', 'l')
    (ec/'Current Conservation 1').rename('current conservation')
    (ec/'Electric Insulation 1').rename('insulation')
    (ec/'Initial Values 1').rename('initial values')
    anode = ec.create('ElectricPotential', 1, name='anode')
    anode.select(anode_surface)
    anode.property('V0', '+U/2*step(t[1/s])')
    cathode = ec.create('ElectricPotential', 1, name='cathode')
    cathode.select(cathode_surface)
    cathode.property('V0', '-U/2*step(t[1/s])')

    materials = model/'materials'
    medium1 = materials.create('Common', name='medium 1')
    medium1.select(model/'selections'/'medium 1')
    (medium1/'Basic').property('relpermittivity',
        ['1', '0', '0', '0', '1', '0', '0', '0', '1'])
    (medium1/'Basic').property('relpermittivity_symmetry', '0')
    (medium1/'Basic').property('electricconductivity',
        ['1e-10', '0', '0', '0', '1e-10', '0', '0', '0', '1e-10'])
    (medium1/'Basic').property('electricconductivity_symmetry', '0')
    medium2 = materials.create('Common', name='medium 2')
    medium2.select(model/'selections'/'medium 2')
    (medium2/'Basic').property('relpermittivity',
        ['2', '0', '0', '0', '2', '0', '0', '0', '2'])
    (medium2/'Basic').property('relpermittivity_symmetry', '0')
    (medium2/'Basic').property('electricconductivity',
        ['1e-10', '0', '0', '0', '1e-10', '0', '0', '0', '1e-10'])
    (medium2/'Basic').property('electricconductivity_symmetry', '0')

    meshes = model/'meshes'
    meshes.create(geometry, name='mesh')

    studies = model/'studies'
    solutions = model/'solutions'
    batches = model/'batches'
    study = studies.create(name='static')
    study.java.setGenPlots(False)
    study.java.setGenConv(False)
    step = study.create('Stationary', name='stationary')
    step.property('activate', [
        physics/'electrostatic', 'on',
        physics/'electric currents', 'off',
        'frame:spatial1', 'on',
        'frame:material1', 'on',
    ])
    solution = solutions.create(name='electrostatic solution')
    solution.java.study(study.tag())
    solution.java.attach(study.tag())
    solution.create('StudyStep', name='equations')
    solution.create('Variables', name='variables')
    solver = solution.create('Stationary', name='stationary solver')
    (solver/'Fully Coupled').rename('fully coupled')
    (solver/'Advanced').rename('advanced options')
    (solver/'Direct').rename('direct solver')
    study = studies.create(name='relaxation')
    study.java.setGenPlots(False)
    study.java.setGenConv(False)
    step = study.create('Transient', name='time-dependent')
    step.property('tlist', 'range(0, 0.01, 1)')
    step.property('activate', [
        physics/'electrostatic', 'off',
        physics/'electric currents', 'on',
        'frame:spatial1', 'on',
        'frame:material1', 'on',
    ])
    solution = solutions.create(name='time-dependent solution')
    solution.java.study(study.tag())
    solution.java.attach(study.tag())
    solution.create('StudyStep', name='equations')
    variables = solution.create('Variables', name='variables')
    variables.property('clist', ['range(0, 0.01, 1)', '0.001[s]'])
    solver = solution.create('Time', name='time-dependent solver')
    solver.property('tlist', 'range(0, 0.01, 1)')
    (solver/'Fully Coupled').rename('fully coupled')
    (solver/'Advanced').rename('advanced options')
    (solver/'Direct').rename('direct solver')
    study = studies.create(name='sweep')
    study.java.setGenPlots(False)
    study.java.setGenConv(False)
    step = study.create('Parametric', name='parameter sweep')
    step.property('pname', ['d'])
    step.property('plistarr', ['1 2 3'])
    step.property('punit', ['mm'])
    step = study.create('Transient', name='time-dependent')
    step.property('activate', [
        physics/'electrostatic', 'off',
        physics/'electric currents', 'on',
        'frame:spatial1', 'on',
        'frame:material1', 'on',
    ])
    step.property('tlist', 'range(0, 0.01, 1)')
    solution = solutions.create(name='parametric solution')
    solution.java.study(study.tag())
    solution.java.attach(study.tag())
    solution.create('StudyStep', name='equations')
    variables = solution.create('Variables', name='variables')
    variables.property('clist', ['range(0, 0.01, 1)', '0.001[s]'])
    solver = solution.create('Time', name='time-dependent solver')
    solver.property('tlist', 'range(0, 0.01, 1)')
    (solver/'Fully Coupled').rename('fully coupled')
    (solver/'Advanced').rename('advanced options')
    (solver/'Direct').rename('direct solver')
    sols = solutions.create(name='parametric solutions')
    sols.java.study(study.tag())
    batch = batches.create('Parametric', name='parametric sweep')
    sequence = batch.create('Solutionseq', name='parametric solution')
    sequence.property('seq', solution)
    sequence.property('psol', sols)
    sequence.property('param', ['"d","0.001"', '"d","0.002"', '"d","0.003"'])
    batch.java.study(study.tag())
    batch.java.attach(study.tag())
    batch.property('control', model/'studies'/'sweep'/'parameter sweep')
    batch.property('pname', ['d'])
    batch.property('plistarr', ['1 2 3'])
    batch.property('punit', ['mm'])
    batch.property('err', True)

    datasets = model/'datasets'
    (datasets/'static//electrostatic solution').rename('electrostatic')
    (datasets/'relaxation//time-dependent solution').rename('time-dependent')
    (datasets/'sweep//parametric solution').rename('sweep/solution')
    (datasets/'sweep//solution').comment(
        'This auto-generated feature could be removed, as it is not '
        'really needed. It was left in the model for the purpose of '
        'testing MPh. Its name contains a forward slash, which MPh '
        'uses to denote parent–child relationships in the node hierarchy.')
    (datasets/'sweep//parametric solutions').rename('parametric sweep')

    tables = model/'tables'
    tables.create('Table', name='electrostatic')
    tables.create('Table', name='time-dependent')
    tables.create('Table', name='parametric')

    evaluations = model/'evaluations'
    evaluation = evaluations.create('EvalGlobal', name='electrostatic')
    evaluation.property('probetag', 'none')
    evaluation.property('table', tables/'electrostatic')
    evaluation.property('expr',  ['2*es.intWe/U^2'])
    evaluation.property('unit',  ['pF'])
    evaluation.property('descr', ['capacitance'])
    evaluation.java.setResult()
    evaluation = evaluations.create('EvalGlobal', name='time-dependent')
    evaluation.property('data', datasets/'time-dependent')
    evaluation.property('probetag', 'none')
    evaluation.property('table', tables/'time-dependent')
    evaluation.property('expr',  ['2*ec.intWe/U^2'])
    evaluation.property('unit',  ['pF'])
    evaluation.property('descr', ['capacitance'])
    evaluation.java.setResult()
    evaluation = evaluations.create('EvalGlobal', name='parametric')
    evaluation.property('data', 'dset4')
    evaluation.property('probetag', 'none')
    evaluation.property('table', tables/'parametric')
    evaluation.property('expr',  ['2*ec.intWe/U^2'])
    evaluation.property('unit',  ['pF'])
    evaluation.property('descr', ['capacitance'])
    evaluation.java.setResult()

    plots = model/'plots'
    plots.java.setOnlyPlotWhenRequested(True)
    plot = plots.create('PlotGroup2D', name='electrostatic field')
    plot.property('titletype', 'manual')
    plot.property('title', 'Electrostatic field')
    plot.property('showlegendsunit', True)
    surface = plot.create('Surface', name='field strength')
    surface.property('resolution', 'normal')
    surface.property('expr', 'es.normE')
    contour = plot.create('Contour', name='equipotentials')
    contour.property('number', 10)
    contour.property('coloring', 'uniform')
    contour.property('colorlegend', False)
    contour.property('color', 'gray')
    contour.property('resolution', 'normal')
    plot = plots.create('PlotGroup2D', name='time-dependent field')
    plot.property('data', datasets/'time-dependent')
    plot.property('titletype', 'manual')
    plot.property('title', 'Time-dependent field')
    plot.property('showlegendsunit', True)
    surface = plot.create('Surface', name='field strength')
    surface.property('expr', 'ec.normE')
    surface.property('resolution', 'normal')
    contour = plot.create('Contour', name='equipotentials')
    contour.property('expr', 'V_ec')
    contour.property('number', 10)
    contour.property('coloring', 'uniform')
    contour.property('colorlegend', False)
    contour.property('color', 'gray')
    contour.property('resolution', 'normal')
    plot = plots.create('PlotGroup1D', name='evolution')
    plot.property('data', datasets/'time-dependent')
    plot.property('titletype', 'manual')
    plot.property('title', 'Evolution of field over time')
    plot.property('xlabel', 't (s)')
    plot.property('xlabelactive', True)
    plot.property('ylabel', '|E| (V/m)')
    plot.property('ylabelactive', True)
    graph = plot.create('PointGraph', name='medium 1')
    graph.select(selections/'probe 1')
    graph.property('expr', 'ec.normE')
    graph.property('linecolor', 'blue')
    graph.property('linewidth', 3)
    graph.property('linemarker', 'point')
    graph.property('markerpos', 'datapoints')
    graph.property('legend', True)
    graph.property('legendmethod', 'manual')
    graph.property('legends', ['medium 1'])
    graph = plot.create('PointGraph', name='medium 2')
    graph.select(selections/'probe 2')
    graph.property('expr', 'ec.normE')
    graph.property('linecolor', 'red')
    graph.property('linewidth', 3)
    graph.property('linemarker', 'point')
    graph.property('markerpos', 'datapoints')
    graph.property('legend', True)
    graph.property('legendmethod', 'manual')
    graph.property('legends', ['medium 2'])
    plot = plots.create('PlotGroup2D', name='sweep')
    plot.property('data', datasets/'parametric sweep')
    plot.property('titletype', 'manual')
    plot.property('title', 'Parameter sweep')
    plot.property('showlegendsunit', True)
    surface = plot.create('Surface', name='field strength')
    surface.property('expr', 'ec.normE')
    surface.property('resolution', 'normal')
    contour = plot.create('Contour', name='equipotentials')
    contour.property('expr', 'V_ec')
    contour.property('number', 10)
    contour.property('coloring', 'uniform')
    contour.property('colorlegend', False)
    contour.property('color', 'gray')
    contour.property('resolution', 'normal')

    exports = model/'exports'
    data = exports.create('Data', name='data')
    data.property('expr', ['es.Ex', 'es.Ey', 'es.Ez'])
    data.property('unit', ['V/m', 'V/m', 'V/m'])
    data.property('descr', ['x-component', 'y-component', 'z-component'])
    data.property('filename', 'data.txt')
    image = exports.create('Image', name='image')
    image.property('sourceobject', plots/'electrostatic field')
    image.property('filename', 'image.png')
    image.property('size', 'manualweb')
    image.property('unit', 'px')
    image.property('height', '720')
    image.property('width', '720')
    image.property('lockratio', 'off')
    image.property('resolution', '96')
    image.property('antialias', 'on')
    image.property('zoomextents', 'off')
    image.property('fontsize', '12')
    image.property('customcolor', [1, 1, 1])
    image.property('background', 'color')
    image.property('gltfincludelines', 'on')
    image.property('title1d', 'on')
    image.property('legend1d', 'on')
    image.property('logo1d', 'on')
    image.property('options1d', 'on')
    image.property('title2d', 'on')
    image.property('legend2d', 'on')
    image.property('logo2d', 'off')
    image.property('options2d', 'on')
    image.property('title3d', 'on')
    image.property('legend3d', 'on')
    image.property('logo3d', 'on')
    image.property('options3d', 'off')
    image.property('axisorientation', 'on')
    image.property('grid', 'on')
    image.property('axes1d', 'on')
    image.property('axes2d', 'on')
    image.property('showgrid', 'on')
    image.property('target', 'file')
    image.property('qualitylevel', '92')
    image.property('qualityactive', 'off')
    image.property('imagetype', 'png')
    image.property('lockview', 'off')

    return model


def needle():
    """Creates model of a needle electrode emitting electrons."""
    model = mph.session.client.create('needle')

    parameters = model/'parameters'
    (parameters/'Parameters 1').rename('parameters')

    parameters = model/'parameters'
    (parameters/'Parameters 1').rename('parameters')
    model.parameter('U', '1[MV]')
    model.description('U', 'applied voltage')
    model.parameter('W', '4.5[eV]')
    model.description('W', 'work function')

    components = model/'components'
    components.create(True, name='component')

    geometries = model/'geometries'
    geometry = geometries.create(3, name='geometry')
    geometry.java.geomRep('comsol')
    cylinder = geometry.create('Cylinder', name='cylinder')
    cylinder.property('pos', ['0', '0', '1.5[mm]'])
    cylinder.property('r', '1[mm]/2')
    cylinder.property('h', '8.5[mm]')
    sphere = geometry.create('Sphere', name='sphere')
    sphere.property('pos', ['0', '0', '1.5[mm]'])
    sphere.property('r', '1[mm]/2')
    union = geometry.create('Union', name='union')
    union.property('intbnd', False)
    union.java.selection('input').set(cylinder.tag(), sphere.tag())
    box = geometry.create('Block', name='box')
    box.property('pos', ['-10[mm]/2', '-10[mm]/2', '0'])
    box.property('size', ['10[mm]', '10[mm]', '10[mm]'])
    model.build(geometry)

    coordinates = model/'coordinates'
    (coordinates/'Boundary System 1').rename('boundary system')

    views = model/'views'
    view = views/'View 1'
    view.rename('view')
    view.java.light('lgt1').label('light 1')
    view.java.light('lgt2').label('light 2')
    view.java.light('lgt3').label('light 3')

    selections = model/'selections'
    domains = selections.create('Explicit', name='domains')
    domains.select('all')
    exterior = selections.create('Adjacent', name='exterior')
    exterior.property('input', [domains])
    electrode = selections.create('Explicit', name='electrode')
    electrode.select(2)
    surface = selections.create('Adjacent', name='surface')
    surface.property('input', [electrode])
    insulation = selections.create('Explicit', name='insulation')
    insulation.java.geom(geometry.tag(), 2)
    insulation.select(4)
    ground = selections.create('Difference', name='ground')
    ground.property('entitydim', 2)
    ground.property('add', [exterior])
    ground.property('subtract', [insulation])
    vacuum = selections.create('Difference', name='vacuum')
    vacuum.property('add', [domains])
    vacuum.property('subtract', [electrode])

    physics = model/'physics'
    field = physics.create('Electrostatics', geometry, name='field')
    field.select(vacuum)
    if model.version() >= '6.3':
        (field/'Free Space 1').rename('free space')
        field.create('ChargeConservationSolid', 3, name='Laplace equation')
        (field/'Laplace equation').select(vacuum)
    else:
        (field/'Charge Conservation 1').rename('Laplace equation')
    (field/'Zero Charge 1').rename('zero charge')
    (field/'Initial Values 1').rename('initial values')
    (field/'Laplace equation').property('epsilonr_mat', 'userdef')
    electrode = field.create('ElectricPotential', 2, name='electrode')
    electrode.select(surface)
    electrode.property('V0', '-U')
    ground = field.create('Ground', 2, name='ground')
    ground.select(selections/'ground')
    electrons = physics.create('ChargedParticleTracing', geometry,
                               name='electrons')
    electrons.select(vacuum)
    (electrons/'Wall 1').rename('walls')
    (electrons/'Particle Properties 1').rename('properties')
    electrons.java.prop('RelativisticCorrection').set('RelativisticCorrection',
                                                      JInt(1))
    emission = electrons.create('Inlet', 2, name='emission')
    emission.select(surface)
    emission.property('InitialPosition', 'Density')
    emission.property('N', 20)
    emission.property('dpro',
        'e_const^3*me_const/(8*pi*me_const*h_const*W) * es.normE^2 * '
        'exp(-4*sqrt(2*me_const*W^3) / (2*hbar_const*e_const*es.normE))')
    emission.property('InitialVelocity', 'KineticEnergyAndDirection')
    emission.property('SpecifyInletTangentialNormal', True)
    emission.property('L0', [[0], [0], [1]])
    emission.property('Ep0', '1[eV]')
    force = electrons.create('ElectricForce', 3, name='force')
    force.select('all')
    force.property('E_src', 'root.comp1.es.Ex')

    meshes = model/'meshes'
    meshes.create(geometry, name='mesh')

    studies = model/'studies'
    study = studies.create(name='study')
    study.java.setGenPlots(False)
    study.java.setGenConv(False)
    step = study.create('BidirectionallyCoupledParticleTracing',
                        name='particle tracing')
    step.property('tlist', 'range(0,1[ps],20[ps])')
    step.property('iter', 1)

    solutions = model/'solutions'
    solution = solutions.create(name='solution')
    solution.java.study(study.tag())
    solution.java.attach(study.tag())
    solution.create('StudyStep', name='equations')
    variables1 = solution.create('Variables', name='variables field')
    variables1.property('control', 'user')
    variables1.property('clist',  ['range(0,1[ps],20[ps])', '2.0E-14[s]'])
    variables1.java.feature('comp1_qcpt').set('solvefor', JBoolean(False))
    solver1 = solution.create('Stationary', name='solver field')
    (solver1/'Direct').rename('direct solver')
    (solver1/'Advanced').rename('advanced options')
    (solver1/'Fully Coupled').rename('fully coupled')
    variables2 = solution.create('Variables', name='variables electrons')
    variables2.property('control', 'user')
    variables2.property('notsolmethod', 'sol')
    variables2.property('notsol', 'sol1')
    variables2.property('notsolnum', 'auto')
    variables2.property('clist', ['range(0,1[ps],20[ps])', '2.0E-14[s]'])
    variables2.java.feature('comp1_V').set('solvefor', JBoolean(False))
    solver2 = solution.create('Time', name='solver electrons')
    (solver2/'Direct').rename('direct solver')
    (solver2/'Advanced').rename('advanced options')
    (solver2/'Fully Coupled').rename('fully coupled')
    solver2.property('tlist', 'range(0,1[ps],20[ps])')
    solver2.property('rtol', 1.0E-7)
    solver2.property('timemethod', 'genalpha')
    solver2.property('estrat', 'exclude')
    solver2.property('tstepsgenalpha', 'strict')
    solver2.property('initialstepgenalpha', '(1.0E-13)[s]')
    solver2.property('initialstepgenalphaactive', True)
    (solver2/'fully coupled').property('ntolfact', 0.1)

    datasets = model/'datasets'
    (datasets/'study//Solution 1').rename('solution')
    datasets.create('Surface', name='surface')
    (datasets/'surface').select(surface)
    datasets.create('Particle', name='electrons')

    plots = model/'plots'
    plots.java.setOnlyPlotWhenRequested(True)
    plot = plots.create('PlotGroup3D', name='plot')
    plot.property('data', datasets/'electrons')
    plot.property('titletype', 'manual')
    plot.property('title', 'Field and trajectories')
    plot.property('showhiddenobjects', True)
    plot.property('frametype', 'spatial')
    plot.property('showlegendsunit', True)
    field = plot.create('Surface', name='field')
    field.property('expr', 'es.normE')
    field.property('data', datasets/'surface')
    field.property('unit', 'kV/mm')
    field.property('resolution', 'normal')
    trajectories = plot.create('ParticleTrajectories', name='trajectories')
    trajectories.property('linetype', 'tube')
    trajectories.property('linecolor', 'yellow')
    trajectories.property('radiusexpr', '0.05[mm]')
    trajectories.property('tuberadiusscaleactive', True)
    trajectories.property('pointtype', 'point')
    trajectories.property('sphereradiusscale', 0.07)
    trajectories.property('sphereradiusscaleactive', False)

    return model

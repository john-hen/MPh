﻿"""Tests the `model` module."""

########################################
# Dependencies                         #
########################################
import mph
import models
from fixtures import logging_disabled
from fixtures import warnings_disabled
from fixtures import setup_logging
from numpy.testing import assert_allclose
from pytest import raises
from pathlib import Path
from platform import system


########################################
# Fixtures                             #
########################################
client = None
model  = None
empty  = None


def setup_module():
    global client, model, empty
    client = mph.start()
    model  = models.capacitor()
    empty  = client.create('empty')


def teardown_module():
    client.clear()
    here = Path(__file__).resolve().parent
    files = (Path('capacitor.mph'), Path('empty.java'),
             here/'capacitor.mph', here/'model.mph',
             here/'model.java', here/'model.m', here/'model.vba',
             here/'data.txt', here/'data.vtu',
             here/'image.png',
             here/'mesh.mphbin', here/'mesh.mphtxt',
             here/'animation.gif', here/'animation.swf',
             here/'animation.avi', here/'animation.webm',
             here/'frame1.png', here/'frame2.png', here/'frame3.png')
    for file in files:
        if file.exists():
            file.unlink()


class Derived(mph.Model):
    pass


########################################
# Tests                                #
########################################


def test_init():
    derived = Derived(model)
    assert derived.java == model.java


def test_str():
    assert str(model) == 'capacitor'


def test_repr():
    assert repr(model) == "Model('capacitor')"


def test_eq():
    assert model == model


def test_truediv():
    assert (model/'functions').name() == 'functions'
    node = model/'functions'/'step'
    assert (model/node).name() == 'step'
    assert (model/None).is_root()
    with logging_disabled(), raises(TypeError):
        model/False


def test_contains():
    assert 'functions' in model
    assert 'functions/step' in model
    assert 'function/non-existing' not in model
    other = client.create('other')
    assert (other/'functions') in model
    assert (other/'functions'/'step') in model
    client.remove(other)


def test_iter():
    assert model/'functions' in list(model)
    assert model/'functions'/'step' not in list(model)


def test_name():
    assert model.name() == 'capacitor'


def test_file():
    assert model.file().name == Path().resolve().name


def test_version():
    assert model.version() == mph.discovery.backend()['name']


def test_functions():
    assert 'step'  in model.functions()


def test_components():
    assert 'component' in model.components()


def test_geometries():
    assert 'geometry' in model.geometries()


def test_selections():
    assert 'domains'  in model.selections()
    assert 'exterior' in model.selections()
    assert 'axis'     in model.selections()
    assert 'center'   in model.selections()


def test_physics():
    assert 'electrostatic'     in model.physics()
    assert 'electric currents' in model.physics()


def test_multiphysics():
    assert model.multiphysics() == []


def test_materials():
    materials = model.materials()
    assert 'medium 1' in materials
    assert 'medium 2' in materials


def test_meshes():
    assert 'mesh' in model.meshes()


def test_studies():
    assert 'static'     in model.studies()
    assert 'relaxation' in model.studies()
    assert 'sweep'      in model.studies()


def test_solutions():
    assert 'electrostatic solution'  in model.solutions()
    assert 'time-dependent solution' in model.solutions()
    assert 'parametric solutions'    in model.solutions()


def test_datasets():
    assert 'electrostatic'    in model.datasets()
    assert 'time-dependent'   in model.datasets()
    assert 'parametric sweep' in model.datasets()


def test_plots():
    assert 'electrostatic field'  in model.plots()
    assert 'time-dependent field' in model.plots()
    assert 'evolution'            in model.plots()
    assert 'sweep'                in model.plots()


def test_exports():
    assert 'data'  in model.exports()
    assert 'image' in model.exports()


def test_modules():
    assert 'Comsol core' in model.modules()
    for value in mph.model.modules.values():
        assert value in mph.client.modules.values()


def test_build():
    model.build()
    model.build('geometry')
    model.build(model/'geometries'/'geometry')
    with logging_disabled():
        with raises(ValueError):
            model.build(model/'function'/'step')
        with raises(LookupError):
            model.build('non-existing')
        with raises(TypeError):
            model.build(False)
        with raises(RuntimeError):
            empty.build()


def test_mesh():
    model.mesh()
    model.mesh('mesh')
    model.mesh(model/'meshes'/'mesh')
    with logging_disabled():
        with raises(ValueError):
            model.mesh(model/'function'/'step')
        with raises(LookupError):
            model.mesh('non-existing')
        with raises(TypeError):
            model.mesh(False)
        with raises(RuntimeError):
            empty.mesh()


def test_solve():
    model.solve()
    model.solve('static')
    model.solve(model/'studies'/'static')
    with logging_disabled():
        with raises(ValueError):
            model.solve(model/'function'/'step')
        with raises(LookupError):
            model.solve('non-existing')
        with raises(TypeError):
            model.solve(False)
        with raises(RuntimeError):
            empty.solve()


def test_inner():
    (indices, values) = model.inner('time-dependent')
    assert indices.dtype.kind == 'i'
    assert values.dtype.kind  == 'f'
    assert (indices == list(range(1,102))).all()
    assert values[0] == 0
    assert values[-1] == 1
    assert model.inner(model/'datasets'/'time-dependent')
    assert model.inner('sweep//solution')
    with logging_disabled():
        with raises(ValueError):
            model.inner('non-existing')
        with raises(TypeError):
            model.inner(False)
        no_solution = (model/'datasets').create('CutPoint2D')
        no_solution.property('data', 'none')
        with raises(RuntimeError):
            model.inner(no_solution)
        no_solution.remove()


def test_outer():
    (indices, values) = model.outer('parametric sweep')
    assert indices.dtype.kind == 'i'
    assert values.dtype.kind  == 'f'
    assert (indices == list(range(1,4))).all()
    assert (values == (1.0, 2.0, 3.0)).all()
    assert model.outer(model/'datasets'/'parametric sweep')
    assert model.outer('sweep//solution')
    with logging_disabled():
        with raises(ValueError):
            model.outer('non-existing')
        with raises(TypeError):
            model.outer(False)
        no_solution = (model/'datasets').create('CutPoint2D')
        no_solution.property('data', 'none')
        with raises(RuntimeError):
            model.outer(no_solution)
        no_solution.remove()


def test_evaluate():
    # Test global evaluation of stationary solution.
    C = model.evaluate('2*es.intWe/U^2', 'pF')
    assert_allclose(C, 0.74, atol=0.01)
    # Test field evaluation of stationary solution.
    (x, y, E) = model.evaluate(['x', 'y', 'es.normE'], ['mm', 'mm', 'V/m'])
    (Emax, xmax, ymax) = (E.max(), x[E.argmax()], y[E.argmax()])
    assert_allclose(Emax, 820, atol=10)
    assert_allclose(abs(xmax), 1.04, atol=0.01)
    assert_allclose(abs(ymax), 4.27, atol=0.01)
    # Test global evaluation of time-dependent solution.
    (dataset, expression, unit) = ('time-dependent', '2*ec.intWe/U^2', 'pF')
    C_first = model.evaluate(expression, unit, dataset, 'first')
    assert_allclose(C_first, 0.74, atol=0.01)
    C_last = model.evaluate(expression, unit, dataset, 'last')
    assert_allclose(C_last, 0.83, atol=0.01)
    C = model.evaluate(expression, unit, dataset)
    assert_allclose(C[0], C_first)
    assert_allclose(C[-1], C_last)
    C = model.evaluate(expression, unit, dataset, inner=[1, 101])
    assert_allclose(C[0], C_first)
    assert_allclose(C[1], C_last)
    # Test field evaluation of time-dependent solution.
    (dataset, expression, unit) = ('time-dependent', 'ec.normD', 'nC/m^2')
    D_first = model.evaluate(expression, unit, dataset, 'first')
    assert_allclose(D_first.max(), 7.2, atol=0.1)
    D_last = model.evaluate(expression, unit, dataset, 'last')
    assert_allclose(D_last.max(), 10.8, atol=0.1)
    D = model.evaluate(expression, unit, dataset)
    assert_allclose(D[0], D_first)
    assert_allclose(D[-1], D_last)
    D = model.evaluate(expression, unit, dataset, inner=[1, 101])
    assert_allclose(D[0], D_first)
    assert_allclose(D[1], D_last)
    # Test global evaluation of parameter sweep.
    (dataset, expression, unit) = ('parametric sweep', '2*ec.intWe/U^2', 'pF')
    C1 = model.evaluate(expression, unit, dataset, 'first', 1)
    assert_allclose(C1, 1.32, atol=0.01)
    C2 = model.evaluate(expression, unit, dataset, 'first', 2)
    assert_allclose(C2, 0.74, atol=0.01)
    C3 = model.evaluate(expression, unit, dataset, 'first', 3)
    assert_allclose(C3, 0.53, atol=0.01)
    # Test field evaluation of parameter sweep.
    (dataset, expression, unit) = ('parametric sweep', 'ec.normD', 'nC/m^2')
    D_first = model.evaluate(expression, unit, dataset, 'first', 2)
    assert_allclose(D_first.max(), 7.2, atol=0.1)
    D_last = model.evaluate(expression, unit, dataset, 'last', 2)
    assert_allclose(D_last.max(), 10.8, atol=0.1)
    D = model.evaluate(expression, unit, dataset, outer=2)
    assert_allclose(D[0], D_first)
    assert_allclose(D[-1], D_last)
    # Test varying time steps in parameter sweep. See issue #112.
    study = model/'studies'/'sweep'
    (study/'time-dependent').property('tlist', 'range(0, 0.01/d[1/mm], 1)')
    model.solve(study)
    assert len(model.evaluate('t', 's', 'parametric sweep', outer=1)) == 101
    assert len(model.evaluate('t', 's', 'parametric sweep', outer=2)) == 201
    assert len(model.evaluate('t', 's', 'parametric sweep', outer=3)) == 301
    # Test evaluation of complex-valued global expressions.
    U = model.evaluate('U')
    z = model.evaluate('U + j*U')
    assert z.real == U
    assert z.imag == U
    # Test evaluation of complex-valued fields.
    (Ex, Ey) = model.evaluate(['es.Ex', 'es.Ey'])
    Z = model.evaluate('es.Ex + j*es.Ey')
    assert (Z.real == Ex).all()
    assert (Z.imag == Ey).all()
    # Test argument "dataset".
    with logging_disabled():
        assert model.evaluate('U')
        assert model.evaluate('U', dataset='electrostatic')
        assert model.evaluate('U', dataset=model/'datasets'/'electrostatic')
        assert model.evaluate('U', dataset='sweep//solution').all()
        with raises(ValueError):
            model.evaluate('U', dataset='non-existing')
        with raises(TypeError):
            model.evaluate('U', dataset=False)
        with raises(RuntimeError):
            empty.evaluate('U')
        no_solution = (model/'datasets').create('CutPoint2D')
        no_solution.property('data', 'none')
        with raises(RuntimeError):
            model.evaluate('U', dataset=no_solution)
        no_solution.remove()
        solution = model/'solutions'/'electrostatic solution'
        solution.java.clearSolution()
        with raises(RuntimeError):
            model.evaluate('U')
        model.solve('static')
    # Test argument "inner".
    with logging_disabled(), raises(TypeError):
        model.evaluate('U', dataset='time-dependent', inner='invalid')
    # Test argument "outer".
    with logging_disabled(), raises(TypeError):
        model.evaluate('U', dataset='parametric sweep', outer='invalid')
    # Test particle tracing (if that add-on module is installed).
    if 'Particle Tracing' in client.modules():
        needle = models.needle()
        needle.solve()
        (qx, qy, qz) = needle.evaluate(['qx', 'qy', 'qz'], dataset='electrons')
        assert qx.shape == (20, 21)
        assert qy.shape == (20, 21)
        assert qz.shape == (20, 21)
        qf = needle.evaluate('qx', dataset='electrons', inner='first')
        assert (qf == qx[:,0]).all()
        ql = needle.evaluate('qx', dataset='electrons', inner='last')
        assert (ql == qx[:,-1]).all()
        qi = needle.evaluate('qx', dataset='electrons', inner=[1,21])
        assert (qi[:,0] == qf).all()
        assert (qi[:,1] == ql).all()
        z = needle.evaluate('qx + j*qy', dataset='electrons')
        assert (z.real == qx).all()
        assert (z.imag == qy).all()


def test_rename():
    name = model.name()
    model.rename('test')
    assert model.name() == 'test'
    model.rename(name)
    assert model.name() == name


def test_parameter():
    value = model.parameter('U')
    model.parameter('U', '2[V]')
    assert model.parameter('U') == '2[V]'
    model.parameter('U', '2')
    assert model.parameter('U') == '2'
    assert model.parameter('U', evaluate=True) == 2
    model.parameter('U', 3)
    assert model.parameter('U') == '3'
    assert model.parameter('U', evaluate=True) == 3
    model.parameter('U', 1+1j)
    assert model.parameter('U') == '(1+1j)'
    assert model.parameter('U', evaluate=True) == 1+1j
    with logging_disabled():
        with raises(ValueError):
            model.parameter('non-existing')
        with raises(RuntimeError):
            model.parameter('non-existing', evaluate=True)
    with warnings_disabled():
        model.parameter('U', '1', 'V')
        assert model.parameter('U') == '1 [V]'
        model.parameter('U', description='applied voltage')
    model.parameter('U', value)
    assert model.parameter('U') == value


def test_parameters():
    assert 'U' in model.parameters()
    assert '1[V]' in model.parameters().values()
    assert ('U', '1[V]') in model.parameters().items()
    assert ('U', 1) in model.parameters(evaluate=True).items()


def test_description():
    assert model.description('U') == 'applied voltage'
    model.description('U', 'test')
    assert model.description('U') == 'test'
    model.description('U', 'applied voltage')
    assert model.description('U') == 'applied voltage'


def test_descriptions():
    assert 'U' in model.descriptions()
    assert 'applied voltage' in model.descriptions().values()
    assert ('U', 'applied voltage') in model.descriptions().items()


def test_property():
    assert model.property('functions/step', 'funcname') == 'step'
    model.property('functions/step', 'funcname', 'renamed')
    assert model.property('functions/step', 'funcname') == 'renamed'
    model.property('functions/step', 'funcname', 'step')
    assert model.property('functions/step', 'funcname') == 'step'
    assert_allclose(model.property('functions/step', 'from'), 0.0)
    model.property('functions/step', 'from', 0.1)
    assert_allclose(model.property('functions/step', 'from'), 0.1)
    model.property('functions/step', 'from', 0.0)
    assert_allclose(model.property('functions/step', 'from'), 0.0)


def test_properties():
    assert 'funcname' in model.properties('functions/step')


def test_create():
    model.create('functions/interpolation', 'Interpolation')
    assert 'interpolation' in model.functions()
    model.create(model/'functions', 'Image')
    assert 'Image 1' in model.functions()


def test_remove():
    model.remove('functions/interpolation')
    assert 'interpolation' not in model.functions()
    model.remove(model/'functions'/'Image 1')
    assert 'Image 1' not in model.functions()


def test_import():
    # Create interpolation function based on external image.
    image = model.create('functions/image', 'Image')
    image.property('funcname', 'im')
    image.property('fununit', '1/m^2')
    image.property('xmin', -5)
    image.property('xmax', +5)
    image.property('ymin', -5)
    image.property('ymax', +5)
    image.property('extrap', 'value')
    # Create interpolation table.
    table = model.create('functions/table', 'Interpolation')
    table.property('funcname', 'f')
    table.property('table', [
        ['+1',   '+2'],
        ['+0.5', '+1'],
        [ '0',    '0'],
        ['-0.5', '-1'],
        ['-1',   '-2'],
    ])
    table.property('interp', 'cubicspline')
    # Import image with file name specified as string and Path.
    here = Path(__file__).resolve().parent
    assert image.property('sourcetype') == 'user'
    model.import_('functions/image', str(here/'gaussian.tif'))
    assert image.property('sourcetype') == 'model'
    image.java.discardData()
    assert image.property('sourcetype') == 'user'
    model.import_(image, here/'gaussian.tif')
    assert image.property('sourcetype') == 'model'
    # Solve with pre-defined boundary condition.
    model.solve('static')
    assert table.property('table')[0] == ['+1', '+2']
    assert table.property('funcname') == 'f'
    old_table = table.property('table')
    old_V0 = model.property('physics/electrostatic/anode', 'V0')
    (y, E) = model.evaluate(['y', 'es.normE'])
    (E_pre, y_pre) = (E.max(), y[E.argmax()])
    # Apply interpolation table defined in model.
    model.property('physics/electrostatic/anode', 'V0', 'U/2 * f(y/l)')
    model.solve('static')
    (y, E) = model.evaluate(['y', 'es.normE'])
    (E_up, y_up) = (E.max(), y[E.argmax()])
    # Import interpolation table with data flipped upside down.
    model.import_(table, here/'table.txt')
    assert table.property('table')[0] == ['+1', '-2']
    table.property('funcname', 'f')
    model.solve('static')
    (y, E) = model.evaluate(['y', 'es.normE'])
    (E_down, y_down) = (E.max(), y[E.argmax()])
    assert E_up - E_down < (E_up + E_down)/1000
    assert y_up + y_down < (y_up - y_down)/1000
    # Re-apply original boundary condition.
    model.property('physics/electrostatic/anode', 'V0', old_V0)
    assert model.property('physics/electrostatic/anode', 'V0') == old_V0
    table.property('table', old_table)
    assert table.property('table') == old_table
    assert table.property('funcname') == 'f'
    model.solve('static')
    (y, E) = model.evaluate(['y', 'es.normE'])
    (E_re, y_re) = (E.max(), y[E.argmax()])
    assert (E_re - E_pre) < 1
    assert (y_re - y_pre) < 0.001
    # Test error handling.
    with logging_disabled():
        with raises(LookupError):
            model.import_('functions/does_not_exist', here/'gaussian.tif')
        with raises(IOError):
            model.import_(image, here/'does_not_exist.tif')
    # Remove test fixtures.
    model.remove('functions/image')
    model.remove('functions/table')


def test_export():
    here = Path(__file__).resolve().parent
    # Test export of text data.
    assert not (here/'data.txt').exists()
    model.export('data', here/'data.txt')
    assert (here/'data.txt').exists()
    (here/'data.txt').unlink()
    assert not (here/'data.txt').exists()
    model.export('data')
    assert (here/'data.txt').exists()
    (here/'data.txt').unlink()
    assert not (here/'data.txt').exists()
    model.export(model/'exports'/'data')
    assert (here/'data.txt').exists()
    (here/'data.txt').unlink()
    assert not (here/'data.txt').exists()
    model.property('exports/data', 'exporttype', 'text')
    model.export('data', here/'data.txt')
    assert (here/'data.txt').exists()
    (here/'data.txt').unlink()
    # Test export of VTK data.
    assert not (here/'data.vtu').exists()
    model.property('exports/data', 'exporttype', 'vtu')
    model.export('data', here/'data.vtu')
    assert (here/'data.vtu').exists()
    (here/'data.vtu').unlink()
    # Test export of images.
    assert not (here/'image.png').exists()
    model.export('image', here/'image.png')
    assert (here/'image.png').exists()
    (here/'image.png').unlink()
    assert not (here/'image.png').exists()
    # Test running all exports at once.
    model.export()
    assert (here/'data.vtu').exists()
    assert (here/'image.png').exists()
    (here/'data.vtu').unlink()
    (here/'image.png').unlink()
    # Test export of meshes.
    mesh = (model/'exports').create('Mesh', name='mesh')
    mesh.java.set('filename', 'mesh')
    assert not (here/'mesh.mphbin').exists()
    model.export('mesh', here/'mesh.mphbin')
    assert (here/'mesh.mphbin').exists()
    (here/'mesh.mphbin').unlink()
    assert not (here/'mesh.mphtxt').exists()
    model.export('mesh', here/'mesh.mphtxt')
    assert (here/'mesh.mphtxt').exists()
    (here/'mesh.mphtxt').unlink()
    mesh.remove()
    # Test export of GIF animations.
    animation = (model/'exports').create('Animation', name='animation')
    animation.property('plotgroup', model/'plots'/'time-dependent field')
    animation.property('looplevelinput', 'manual')
    animation.property('looplevel', [1, 2, 3])
    assert not (here/'animation.gif').exists()
    model.export(animation, here/'animation.gif')
    assert (here/'animation.gif').exists()
    (here/'animation.gif').unlink()
    animation.remove()
    # Test export of AVI movies (which Comsol only supports on Windows).
    if system() == 'Windows':
        animation = (model/'exports').create('Animation', name='animation')
        animation.property('plotgroup', model/'plots'/'time-dependent field')
        animation.property('looplevelinput', 'manual')
        animation.property('looplevel', [1, 2, 3])
        assert not (here/'animation.avi').exists()
        model.export(animation, here/'animation.avi')
        assert (here/'animation.avi').exists()
        (here/'animation.avi').unlink()
        animation.remove()
    # Test export of WebM movies.
    animation = (model/'exports').create('Animation', name='animation')
    animation.property('plotgroup', model/'plots'/'time-dependent field')
    animation.property('looplevelinput', 'manual')
    animation.property('looplevel', [1, 2, 3])
    assert not (here/'animation.webm').exists()
    model.export(animation, here/'animation.webm')
    assert (here/'animation.webm').exists()
    (here/'animation.webm').unlink()
    animation.remove()
    # Test export of image sequences.
    animation = (model/'exports').create('Animation', name='animation')
    animation.property('plotgroup', model/'plots'/'time-dependent field')
    animation.property('looplevelinput', 'manual')
    animation.property('looplevel', [1, 2, 3])
    assert not (here/'frame1.png').exists()
    assert not (here/'frame2.png').exists()
    assert not (here/'frame3.png').exists()
    model.export(animation, here/'frame.png')
    assert (here/'frame1.png').exists()
    assert (here/'frame2.png').exists()
    assert (here/'frame3.png').exists()
    (here/'frame1.png').unlink()
    (here/'frame2.png').unlink()
    (here/'frame3.png').unlink()
    animation.remove()
    # Test error conditions.
    with logging_disabled():
        with raises(ValueError):
            model.export('non-existing')
        animation = (model/'exports').create('Animation', name='animation')
        with raises(ValueError):
            model.export(animation, here/'animation.invalid')
        animation.remove()
        with raises(TypeError):
            model.export(model/'functions'/'step', file='irrelevant.txt')
        with raises(RuntimeError):
            model.export(model/'coordinates'/'boundary system')


def test_clear():
    model.clear()


def test_reset():
    model.reset()


def test_save():
    here = Path(__file__).resolve().parent
    model.save()
    empty.save(format='java')
    assert Path(f'{model}.mph').exists()
    assert Path(f'{empty}.java').exists()
    Path(f'{empty}.java').unlink()
    model.save(here)
    model.save(here, format='java')
    assert (here/f'{model}.mph').exists()
    assert (here/f'{model}.java').exists()
    (here/f'{model}.java').unlink()
    model.save(here/'model.mph')
    model.save()
    assert (here/'model.mph').read_text(errors='ignore').startswith('PK')
    model.save(here/'model.java')
    assert (here/'model.java').exists()
    assert 'public static void main' in (here/'model.java').read_text()
    (here/'model.java').unlink()
    assert not (here/'model.java').exists()
    model.save(format='java')
    assert (here/'model.java').exists()
    (here/'model.java').unlink()
    model.save(here/'model.m')
    assert (here/'model.m').exists()
    assert 'function out = model' in (here/'model.m').read_text()
    (here/'model.m').unlink()
    model.save(here/'model.vba')
    assert (here/'model.vba').exists()
    assert 'Sub run()' in (here/'model.vba').read_text()
    (here/'model.vba').unlink()
    with logging_disabled():
        with raises(ValueError):
            model.save('model.invalid')
        with raises(ValueError):
            model.save('model.mph', format='invalid')


def test_problems():
    assert not model.problems()
    anode = model/'physics'/'electrostatic'/'anode'
    anode.property('V0', '+Ua/2')
    study = model/'studies'/'static'
    try:
        study.run()
    except Exception:
        pass
    assert model.problems()
    anode.property('V0', '+U/2')
    study.run()
    assert not model.problems()


def test_features():
    with warnings_disabled():
        assert 'Laplace equation' in model.features('electrostatic')
        assert 'zero charge'      in model.features('electrostatic')
        assert 'initial values'   in model.features('electrostatic')
        assert 'anode'            in model.features('electrostatic')
        assert 'cathode'          in model.features('electrostatic')
        with logging_disabled(), raises(LookupError):
            model.features('non-existing')


def test_toggle():
    with warnings_disabled():
        model.solve('static')
        assert abs(model.evaluate('V_es').mean()) < 0.1
        model.toggle('electrostatic', 'cathode')
        model.solve('static')
        assert abs(model.evaluate('V_es').mean() - 0.5) < 0.1
        model.toggle('electrostatic', 'cathode', 'on')
        model.solve('static')
        assert abs(model.evaluate('V_es').mean()) < 0.1
        model.toggle('electrostatic', 'cathode', 'off')
        model.solve('static')
        assert abs(model.evaluate('V_es').mean() - 0.5) < 0.1
        with logging_disabled():
            with raises(LookupError):
                model.toggle('non-existing', 'feature')
            with raises(LookupError):
                model.toggle('electrostatic', 'non-existing')


def test_load():
    with warnings_disabled():
        image = model.create('functions/image', 'Image')
        image.property('funcname', 'im')
        image.property('fununit', '1/m^2')
        image.property('xmin', -5)
        image.property('xmax', +5)
        image.property('ymin', -5)
        image.property('ymax', +5)
        image.property('extrap', 'value')
        model.load('gaussian.tif', 'image')
        model.remove('functions/image')
        with logging_disabled(), raises(LookupError):
            model.load('image.png', 'non-existing')


########################################
# Main                                 #
########################################

if __name__ == '__main__':
    setup_logging()
    setup_module()

    try:
        test_str()
        test_repr()
        test_eq()
        test_truediv()
        test_contains()
        test_iter()

        test_name()
        test_file()
        test_version()
        test_functions()
        test_components()
        test_geometries()
        test_selections()
        test_physics()
        test_multiphysics()
        test_materials()
        test_meshes()
        test_studies()
        test_solutions()
        test_datasets()
        test_plots()
        test_exports()
        test_modules()

        test_build()
        test_mesh()
        test_solve()

        test_inner()
        test_outer()
        test_evaluate()

        test_rename()
        test_parameter()
        test_parameters()
        test_description()
        test_descriptions()
        test_property()
        test_properties()
        test_create()
        test_remove()

        test_import()
        test_export()
        test_clear()
        test_reset()
        test_save()

        test_problems()

        test_features()
        test_toggle()
        test_load()

    finally:
        teardown_module()

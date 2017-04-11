from .helper_helper import *
from .helper_helper import _time

from collections import OrderedDict

@unittest.skipUnless( os.environ.get('TEST_HISTOGRAM','true').lower()=='true', 'skipping histogram' )
class HistogramHelper(Chai):

  def setUp(self):
    super(HistogramHelper,self).setUp()

    self.series = Timeseries(self.client, type='histogram', prefix='kairos',
      read_func=int,
      intervals={
        'minute' : {
          'step' : 60,
          'steps' : 5,
        },
        'hour' : {
          'step' : 3600,
          'resolution' : 60,
        }
      } )
    self.series.delete_all()

  def tearDown(self):
    self.series.delete_all()
  
  def test_bulk_insert(self):
    inserts = {
      None      : { 'test1':[1,2,3], 'test2':[4,5,6] },
      _time(0)  : { 'test1':[1,2,3], 'test2':[4,5,6], 'test3':[7,8,9] },
      _time(30) : { 'test1':[1,2,3], 'test2':[4,5,6] },
      _time(60) : { 'test1':[1,2,3], 'test3':[7,8,9] }
    }
    self.series.bulk_insert( inserts )

    t1_i1 = self.series.get('test1', 'minute', timestamp=_time(0))
    assert_equals( {1:2, 2:2, 3:2}, t1_i1[_time(0)] )

    t2_i1 = self.series.get('test2', 'minute', timestamp=_time(0))
    assert_equals( {4:2, 5:2, 6:2}, t2_i1[_time(0)] )
    
    t3_i1 = self.series.get('test3', 'minute', timestamp=_time(0))
    assert_equals( {7:1, 8:1, 9:1}, t3_i1[_time(0)] )

    t1_i2 = self.series.get('test1', 'minute', timestamp=_time(60))
    assert_equals( {1:1, 2:1, 3:1}, t1_i2[_time(60)] )

  def test_bulk_insert_intervals_after(self):
    a,b,c,d,e,f = 10,11,12,13,14,15
    inserts = OrderedDict( (
      (None     , { 'test1':[1,2,3], 'test2':[4,5,6] } ),
      (_time(0) , { 'test1':[1,2,3], 'test2':[4,5,6], 'test3':[7,8,9] } ),
      (_time(30), { 'test1':[1,2,3], 'test2':[4,5,6] } ),
      (_time(60), { 'test1':[a,b,c], 'test3':[d,e,f] })
    ) )
    self.series.bulk_insert( inserts, intervals=3 )

    t1_i1 = self.series.get('test1', 'minute', timestamp=_time(0))
    assert_equals( {1:2, 2:2, 3:2}, t1_i1[_time(0)] )

    t2_i1 = self.series.get('test2', 'minute', timestamp=_time(0))
    assert_equals( {4:2, 5:2, 6:2}, t2_i1[_time(0)] )
    
    t3_i1 = self.series.get('test3', 'minute', timestamp=_time(0))
    assert_equals( {7:1, 8:1, 9:1}, t3_i1[_time(0)] )

    t1_i2 = self.series.get('test1', 'minute', timestamp=_time(60))
    assert_equals( {1:2, 2:2, 3:2, a:1, b:1, c:1}, t1_i2[_time(60)] )

    t3_i3 = self.series.get('test3', 'minute', timestamp=_time(120))
    assert_equals( {7:1, 8:1, 9:1, d:1, e:1, f:1}, t3_i3[_time(120)] )

    t3_i4 = self.series.get('test3', 'minute', timestamp=_time(180))
    assert_equals( {7:1, 8:1, 9:1, d:1, e:1, f:1}, t3_i4[_time(180)] )

  def test_bulk_insert_intervals_before(self):
    a,b,c,d,e,f = 10,11,12,13,14,15
    inserts = OrderedDict( (
      (None     , { 'test1':[1,2,3], 'test2':[4,5,6] } ),
      (_time(0) , { 'test1':[1,2,3], 'test2':[4,5,6], 'test3':[7,8,9] } ),
      (_time(30), { 'test1':[1,2,3], 'test2':[4,5,6] } ),
      (_time(60), { 'test1':[a,b,c], 'test3':[d,e,f] })
    ) )
    self.series.bulk_insert( inserts, intervals=-3 )

    t1_i1 = self.series.get('test1', 'minute', timestamp=_time(0))
    assert_equals( {1:2, 2:2, 3:2, a:1, b:1, c:1}, t1_i1[_time(0)] )

    t2_i1 = self.series.get('test2', 'minute', timestamp=_time(0))
    assert_equals( {4:2, 5:2, 6:2}, t2_i1[_time(0)] )
    
    t3_i1 = self.series.get('test3', 'minute', timestamp=_time(0))
    assert_equals( {7:1, 8:1, 9:1, d:1, e:1, f:1}, t3_i1[_time(0)] )

    t1_i2 = self.series.get('test1', 'minute', timestamp=_time(-60))
    assert_equals( {1:2, 2:2, 3:2, a:1, b:1, c:1}, t1_i2[_time(-60)] )

    t3_i3 = self.series.get('test3', 'minute', timestamp=_time(-120))
    assert_equals( {7:1, 8:1, 9:1, d:1, e:1, f:1}, t3_i3[_time(-120)] )

    t3_i4 = self.series.get('test3', 'minute', timestamp=_time(-180))
    assert_equals( {7:1, 8:1, 9:1}, t3_i4[_time(-180)] )

  def test_get(self):
    # 2 hours worth of data, value is same asV timestamp
    for t in range(1, 7200):
      self.series.insert( 'test', int(t/2), timestamp=_time(t) )

    ###
    ### no resolution, condensed has no impact
    ###
    # middle of an interval
    interval = self.series.get( 'test', 'minute', timestamp=_time(100) )
    assert_equals( [_time(60)], list(interval.keys()) )
    keys = list(range(30,60))
    assert_equals( keys, list(interval[_time(60)].keys()) )
    for k in keys:
      assert_equals( 2, interval[_time(60)][k] )

    # no matching interval, returns no with empty value list
    interval = self.series.get( 'test', 'minute' )
    assert_equals( 1, len(interval) )
    assert_equals( 0, len(list(interval.values())[0]) )
    
    ###
    ### with resolution, optionally condensed
    ###
    interval = self.series.get( 'test', 'hour', timestamp=_time(100) )
    keys = list(range(30,60))
    assert_equals( 60, len(interval) )
    assert_equals( keys, list(interval[_time(60)].keys()) )
    
    interval = self.series.get( 'test', 'hour', timestamp=_time(100), condensed=True )
    assert_equals( 1, len(interval) )
    assert_equals( list(range(0,1800)), list(interval[_time(0)].keys()) )

  def test_get_joined(self):
    # put some data in the first minutes of each hour for test1, and then for
    # a few more minutes in test2
    for t in range(1, 120):
      self.series.insert( 'test1', t, timestamp=_time(t) )
      self.series.insert( 'test2', t, timestamp=_time(t) )
    for t in range(3600, 3720):
      self.series.insert( 'test1', t, timestamp=_time(t) )
      self.series.insert( 'test2', t, timestamp=_time(t) )
    for t in range(120, 240):
      self.series.insert( 'test1', t, timestamp=_time(t) )
    for t in range(3721, 3840):
      self.series.insert( 'test1', t, timestamp=_time(t) )

    ###
    ### no resolution, condensed has no impact
    ###
    # interval with 2 series worth of data
    interval = self.series.get( ['test1','test2'], 'minute', timestamp=_time(100) )
    assert_equals( [_time(60)], list(interval.keys()) )
    assert_equals( dict.fromkeys(range(60,120),2), interval[_time(60)] )

    # interval with 1 series worth of data
    interval = self.series.get( ['test1','test2'], 'minute', timestamp=_time(122) )
    assert_equals( [_time(120)], list(interval.keys()) )
    assert_equals( dict.fromkeys(range(120,180),1), interval[_time(120)] )

    # no matching interval, returns no with empty value list
    interval = self.series.get( ['test1','test2'], 'minute' )
    assert_equals( 1, len(interval) )
    assert_equals( 0, len(list(interval.values())[0]) )

    ###
    ### with resolution, optionally condensed
    ###
    interval = self.series.get( ['test1','test2'], 'hour', timestamp=_time(100) )
    assert_equals( list(map(_time,[0,60,120,180])), list(interval.keys()) )
    assert_equals( dict.fromkeys(range(1,60), 2), interval[_time(0)] )
    assert_equals( dict.fromkeys(range(60,120), 2), interval[_time(60)] )
    assert_equals( dict.fromkeys(range(120,180), 1), interval[_time(120)] )
    assert_equals( dict.fromkeys(range(180,240), 1), interval[_time(180)] )

    data = dict.fromkeys(range(1,120), 2)
    data.update( dict.fromkeys(range(120,240),1) )
    interval = self.series.get( ['test1','test2'], 'hour', timestamp=_time(100), condensed=True )
    assert_equals( [_time(0)], list(interval.keys()) )
    assert_equals( data, interval[_time(0)] )

    # with transforms
    interval = self.series.get( ['test1','test2'], 'hour', timestamp=_time(100), transform='count' )
    assert_equals( 120, interval[_time(60)] )

    interval = self.series.get( ['test1','test2'], 'hour', timestamp=_time(100), transform=['min','max','count'], condensed=True )
    assert_equals( {'min':1, 'max':239, 'count':358}, interval[_time(0)] )

  def test_series(self):
    # 2 hours worth of data, value is same asV timestamp
    for t in range(1, 7200):
      self.series.insert( 'test', int(t/2), timestamp=_time(t) )

    ###
    ### no resolution, condensed has no impact
    ###
    interval = self.series.series( 'test', 'minute', end=_time(250) )
    assert_equals( list(map(_time, [0,60,120,180,240])), list(interval.keys()) )
    assert_equals( list(range(0,30)), sorted(interval[_time(0)].keys()) )
    assert_equals( 1, interval[_time(0)][0] )
    for k in range(1,30):
      assert_equals(2, interval[_time(0)][k])
    assert_equals( list(range(120,150)), sorted(interval[_time(240)].keys()) )
    for k in range(120,150):
      assert_equals(2, interval[_time(240)][k])
    
    interval = self.series.series( 'test', 'minute', steps=2, end=_time(250) )
    assert_equals( list(map(_time, [180,240])), list(interval.keys()) )
    assert_equals( list(range(120,150)), sorted(interval[_time(240)].keys()) )

    # with collapsed
    interval = self.series.series( 'test', 'minute', end=_time(250), collapse=True )
    assert_equals( list(map(_time, [0])), list(interval.keys()) )
    assert_equals( list(range(0,150)), sorted(interval[_time(0)].keys()) )
    for k in range(1,150):
      assert_equals(2, interval[_time(0)][k])
    
    ###
    ### with resolution
    ###
    interval = self.series.series( 'test', 'hour', end=_time(250) )
    assert_equals( 1, len(interval) )
    assert_equals( 60, len(interval[_time(0)]) )
    assert_equals( list(range(0,30)), sorted(interval[_time(0)][_time(0)].keys()) )

    # single step, last one    
    interval = self.series.series( 'test', 'hour', condensed=True, end=_time(4200) )
    assert_equals( 1, len(interval) )
    assert_equals( 1800, len(interval[_time(3600)]) )
    assert_equals( list(range(1800,3600)), sorted(interval[_time(3600)].keys()) )

    interval = self.series.series( 'test', 'hour', condensed=True, end=_time(4200), steps=2 )
    assert_equals( list(map(_time, [0,3600])), list(interval.keys()) )
    assert_equals( 1800, len(interval[_time(0)]) )
    assert_equals( 1800, len(interval[_time(3600)]) )
    assert_equals( list(range(1800,3600)), sorted(interval[_time(3600)].keys()) )

    # with collapsed
    interval = self.series.series( 'test', 'hour', condensed=True, end=_time(4200), steps=2, collapse=True )
    assert_equals( list(map(_time, [0])), list(interval.keys()) )
    assert_equals( 3600, len(interval[_time(0)]) )
    assert_equals( list(range(0,3600)), sorted(interval[_time(0)].keys()) )

  def test_series_joined(self):
    # put some data in the first minutes of each hour for test1, and then for
    # a few more minutes in test2
    for t in range(1, 120):
      self.series.insert( 'test1', t, timestamp=_time(t) )
      self.series.insert( 'test2', t, timestamp=_time(t) )
    for t in range(3600, 3720):
      self.series.insert( 'test1', t, timestamp=_time(t) )
      self.series.insert( 'test2', t, timestamp=_time(t) )
    for t in range(120, 240):
      self.series.insert( 'test1', t, timestamp=_time(t) )
    for t in range(3720, 3840):
      self.series.insert( 'test1', t, timestamp=_time(t) )

    ###
    ### no resolution, condensed has no impact
    ###
    interval = self.series.series( ['test1','test2'], 'minute', end=_time(250) )
    assert_equals( list(map(_time,[0,60,120,180,240])), list(interval.keys()) )
    assert_equals( dict.fromkeys(range(1,60), 2), interval[_time(0)] )
    assert_equals( dict.fromkeys(range(60,120), 2), interval[_time(60)] )
    assert_equals( dict.fromkeys(range(120,180), 1), interval[_time(120)] )
    assert_equals( dict.fromkeys(range(180,240), 1), interval[_time(180)] )
    assert_equals( {}, interval[_time(240)] )

    # no matching interval, returns no with empty value list
    interval = self.series.series( ['test1','test2'], 'minute', start=time.time(), steps=2 )
    assert_equals( 2, len(interval) )
    assert_equals( {}, list(interval.values())[0] )

    # with transforms
    interval = self.series.series( ['test1','test2'], 'minute', end=_time(250), transform=['min','count'] )
    assert_equals( list(map(_time,[0,60,120,180,240])), list(interval.keys()) )
    assert_equals( {'min':1, 'count':118}, interval[_time(0)] )
    assert_equals( {'min':60, 'count':120}, interval[_time(60)] )
    assert_equals( {'min':120, 'count':60}, interval[_time(120)] )
    assert_equals( {'min':180, 'count':60}, interval[_time(180)] )
    assert_equals( {'min':0, 'count':0}, interval[_time(240)] )

    # with collapsed
    data = dict.fromkeys(range(1,120), 2)
    data.update( dict.fromkeys(range(120,240), 1) )
    interval = self.series.series( ['test1','test2'], 'minute', end=_time(250), collapse=True )
    assert_equals( [_time(0)], list(interval.keys()) )
    assert_equals( data, interval[_time(0)] )

    # with tranforms and collapsed
    interval = self.series.series( ['test1','test2'], 'minute', end=_time(250), transform=['min','max', 'count'], collapse=True )
    assert_equals( [_time(0)], list(interval.keys()) )
    assert_equals( {'min':1, 'max':239, 'count':358}, interval[_time(0)] )

    ###
    ### with resolution, optionally condensed
    ###
    interval = self.series.series( ['test1','test2'], 'hour', end=_time(250) )
    assert_equals( 1, len(interval) )
    assert_equals( list(map(_time,[0,60,120,180])), list(interval[_time(0)].keys()) )
    assert_equals( 4, len(interval[_time(0)]) )
    assert_equals( dict.fromkeys(range(1,60), 2), interval[_time(0)][_time(0)] )
    assert_equals( dict.fromkeys(range(60,120), 2), interval[_time(0)][_time(60)] )
    assert_equals( dict.fromkeys(range(120,180), 1), interval[_time(0)][_time(120)] )
    assert_equals( dict.fromkeys(range(180,240), 1), interval[_time(0)][_time(180)] )

    # condensed
    data = dict.fromkeys(range(1,120), 2)
    data.update( dict.fromkeys(range(120,240), 1) )
    interval = self.series.series( ['test1','test2'], 'hour', end=_time(250), condensed=True )
    assert_equals( [_time(0)], list(interval.keys()) )
    assert_equals( data, interval[_time(0)] )

    # with collapsed across multiple intervals
    data = dict.fromkeys(range(1,120), 2)
    data.update( dict.fromkeys(range(120,240), 1) )
    data.update( dict.fromkeys(range(3600,3720), 2) )
    data.update( dict.fromkeys(range(3720,3840), 1) )
    interval = self.series.series( ['test1','test2'], 'hour', condensed=True, end=_time(4200), steps=2, collapse=True )
    assert_equals( list(map(_time, [0])), list(interval.keys()) )
    assert_equals( data, interval[_time(0)] )

    # with transforms collapsed
    interval = self.series.series( ['test1','test2'], 'hour', condensed=True, end=_time(4200), steps=2, collapse=True, transform=['min','max','count'] )
    assert_equals( list(map(_time, [0])), list(interval.keys()) )
    assert_equals( {'min':1,'max':3839,'count':718}, interval[_time(0)] )

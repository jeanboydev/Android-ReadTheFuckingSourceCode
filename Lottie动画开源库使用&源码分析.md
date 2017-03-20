# Lottie动画库的使用 #

## 简介 ##


https://github.com/airbnb/lottie-android

Lottie是Airbnb开源的动画项目，它能够同时支持iOS,Android与ReactNative的开发，使用流程如下图所示


![图片1][1]

如图所示，通过安装AE上的bodymovin的插件，能够将AE中的动画工程文件转换为通用的json格式描述文件(bodymovin插件本身是用于网页上呈现各种AE效果的一个开源库),lottie所做的事情就是实现在不同移动端平台上呈现AE动画的方式，从而达到动画文件的一次绘制、一次转换，随处可用的效果，这个跟Java一次编译随处运行效果一样

## 使用方式 ##
1.导入

```Xml
dependencies {  
  compile 'com.airbnb.android:lottie:1.5.3'
}
```

2.布局文件中添加
```Xml
<com.airbnb.lottie.LottieAnimationView
        android:id="@+id/animation_view"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        app:lottie_fileName="hello-world.json"
        app:lottie_loop="true"
        app:lottie_autoPlay="true" />
```
3.代码调用
```Java
LottieAnimationView animationView = (LottieAnimationView) findViewById(R.id.animation_view);
animationView.setAnimation("hello-world.json");
animationView.loop(true);
```
4.动画监听
```Java
animationView.addAnimatorUpdateListener((animation) -> {
// Do something.
});
animationView.playAnimation();
...
if (animationView.isAnimating()) {
    // Do something.
}
...
animationView.setProgress(0.5f);
...
// 自定义速度与时长
ValueAnimator animator = ValueAnimator.ofFloat(0f, 1f)
    .setDuration(500);
animator.addUpdateListener(animation -> {
    animationView.setProgress(animation.getAnimatedValue());
});
animator.start();
...
animationView.cancelAnimation();
```
## 关于性能 ##
官方说法

- 如果没有mask(一种动画)和mattes(蒙版)，那么性能和内存非常好，没有bitmap创建，大部分操作都是简单的cavas绘制。<br/>
- 如果存在mattes，将会创建2～3个bitmap。bitmap在动画加载到window时被创建，被window删除时回收。<br/>
所以不宜在RecyclerView中使用包涵mattes或者mask的动画，否则会引起bitmap抖动。<br/>
除了内存抖动，mattes和mask中必要的bitmap.eraseColor()和canvas.drawBitmap()也会降低动画性能。<br/>
对于简单的动画，在实际使用时性能不太明显。<br/>
- 如果在列表中使用动画，推荐使用缓存LottieAnimationView.setAnimation(String, CacheStrategy) 。

## 原理 ##
Lottie使用json文件来作为动画数据源，json文件是通过Bodymovin插件导出的，查看sample中给出的json文件，其实就是把图片中的元素进行来拆分，并且描述每个元素的动画执行路径和执行时间。Lottie的功能就是读取这些数据，然后绘制到屏幕上。

![图片2][2]

### 1.解析json文件 ###
首先要解析json，建立数据到对象的映射，然后根据数据对象创建合适的Drawable绘制到view上，动画的实现可以通过操作读取到的元素完成。

![图片3][3]


- LottieComposition (json->数据对象)

Lottie使用LottieComposition来作为After Effects的数据对象，即把Json文件映射为到LottieComposition，该类中提供了解析json的静态方法。
```Java
static LottieComposition fromJsonSync(Resources res, JSONObject json) {
  Rect bounds = null;
  float scale = res.getDisplayMetrics().density;
  int width = json.optInt("w", -1);
  int height = json.optInt("h", -1);

  if (width != -1 && height != -1) {
    int scaledWidth = (int) (width * scale);
    int scaledHeight = (int) (height * scale);
    bounds = new Rect(0, 0, scaledWidth, scaledHeight);
  }

  long startFrame = json.optLong("ip", 0);
  long endFrame = json.optLong("op", 0);
  int frameRate = json.optInt("fr", 0);
  LottieComposition composition =
      new LottieComposition(bounds, startFrame, endFrame, frameRate, scale);
  JSONArray assetsJson = json.optJSONArray("assets");
  parseImages(assetsJson, composition);
  parsePrecomps(assetsJson, composition);
  parseLayers(json, composition);
  return composition;
}

private static void parseLayers(JSONObject json, LottieComposition composition) {
  JSONArray jsonLayers = json.optJSONArray("layers");
  int length = jsonLayers.length();
  for (int i = 0; i < length; i++) {
    Layer layer = Layer.Factory.newInstance(jsonLayers.optJSONObject(i), composition);
    addLayer(composition.layers, composition.layerMap, layer);
  }
}
```

### 2.数据对象到Drawable的映射 ###
LottieDrawable 继承自 AnimatableLayer 继承自 Drawable


AnimatableLayer
> 首先看下AnimatableLayer继承了Drawable主要重写了draw，在代码中可以看出，借用canvas的save、restoreToCount来实现像PS那种图层叠加的效果。

```Java
 @Override
  public void draw(@NonNull Canvas canvas) {
    int saveCount = canvas.save();
    applyTransformForLayer(canvas, this);

    int backgroundAlpha = Color.alpha(backgroundColor);
    if (backgroundAlpha != 0) {
      int alpha = backgroundAlpha;
      if (this.transform != null) {
        alpha = alpha * this.transform.getOpacity().getValue() / 255;
      }
      solidBackgroundPaint.setAlpha(alpha);
      if (alpha > 0) {
        canvas.drawRect(getBounds(), solidBackgroundPaint);
      }
    }
    for (int i = 0; i < layers.size(); i++) {
      layers.get(i).draw(canvas);
    }
    canvas.restoreToCount(saveCount);
  }
```

LottieDrawable
```Java
boolean setComposition(LottieComposition composition) {
    if (getCallback() == null) {
      throw new IllegalStateException(
          "You or your view must set a Drawable.Callback before setting the composition. This " +
              "gets done automatically when added to an ImageView. " +
              "Either call ImageView.setImageDrawable() before setComposition() or call " +
              "setCallback(yourView.getCallback()) first.");
    }

    if (this.composition == composition) {
      return false;
    }

    clearComposition();
    this.composition = composition;
    setSpeed(speed);
    setBounds(0, 0, composition.getBounds().width(), composition.getBounds().height());
    buildLayersForComposition(composition);

    setProgress(getProgress());
    return true;
  }
```
该方法在LottieAnimationView中调用，该方法中实际调用的核心函数是
>  void buildLayersForComposition(LottieComposition composition)

```Java
private void buildLayersForComposition(LottieComposition composition) {
    if (composition == null) {
      throw new IllegalStateException("Composition is null");
    }
    LongSparseArray<LayerView> layerMap = new LongSparseArray<>(composition.getLayers().size());
    List<LayerView> layers = new ArrayList<>(composition.getLayers().size());
    LayerView mattedLayer = null;
    for (int i = composition.getLayers().size() - 1; i >= 0; i--) {
      Layer layer = composition.getLayers().get(i);
      LayerView layerView;
      layerView = new LayerView(layer, composition, this, canvasPool);
      layerMap.put(layerView.getId(), layerView);
      if (mattedLayer != null) {
        mattedLayer.setMatteLayer(layerView);
        mattedLayer = null;
      } else {
        layers.add(layerView);
        if (layer.getMatteType() == Layer.MatteType.Add) {
          mattedLayer = layerView;
        } else if (layer.getMatteType() == Layer.MatteType.Invert) {
          mattedLayer = layerView;
        }
      }
    }

    for (int i = 0; i < layers.size(); i++) {
      LayerView layerView = layers.get(i);
      addLayer(layerView);
    }

    for (int i = 0; i < layerMap.size(); i++) {
      long key = layerMap.keyAt(i);
      LayerView layerView = layerMap.get(key);
      LayerView parentLayer = layerMap.get(layerView.getLayerModel().getParentId());
      if (parentLayer != null) {
        layerView.setParentLayer(parentLayer);
      }
    }
  }
```
### 3. 绘制 ###
LottieAnimationView 继承自 AppCompatImageView，封装了一些动画的操作
```Java
public class LottieAnimationView extends AppCompatImageView {

 
  private final LottieDrawable lottieDrawable = new LottieDrawable();
  
  @Nullable private LottieComposition composition;

  public LottieAnimationView(Context context) {
    super(context);
    init(null);
  }

  public LottieAnimationView(Context context, AttributeSet attrs) {
    super(context, attrs);
    init(attrs);
  }

  public LottieAnimationView(Context context, AttributeSet attrs, int defStyleAttr) {
    super(context, attrs, defStyleAttr);
    init(attrs);
  }

  private void init(@Nullable AttributeSet attrs) {
    TypedArray ta = getContext().obtainStyledAttributes(attrs, R.styleable.LottieAnimationView);
    String fileName = ta.getString(R.styleable.LottieAnimationView_lottie_fileName);
    if (!isInEditMode() && fileName != null) {
      setAnimation(fileName);
    }
    if (ta.getBoolean(R.styleable.LottieAnimationView_lottie_autoPlay, false)) {
      lottieDrawable.playAnimation();
    }
    lottieDrawable.loop(ta.getBoolean(R.styleable.LottieAnimationView_lottie_loop, false));
    setImageAssetsFolder(ta.getString(R.styleable.LottieAnimationView_lottie_imageAssetsFolder));
    int cacheStrategy = ta.getInt(
        R.styleable.LottieAnimationView_lottie_cacheStrategy,
        CacheStrategy.None.ordinal());
    defaultCacheStrategy = CacheStrategy.values()[cacheStrategy];
    ta.recycle();
    setLayerType(LAYER_TYPE_SOFTWARE, null);

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR1) {
    float systemAnimationScale = Settings.Global.getFloat(getContext().getContentResolver(),
        Settings.Global.ANIMATOR_DURATION_SCALE, 1.0f);
      if (systemAnimationScale == 0f) {
        lottieDrawable.systemAnimationsAreDisabled();
      }
    }
  }

  public void playAnimation() {
    lottieDrawable.playAnimation();
  }

  @SuppressWarnings("unused") public void reverseAnimation() {
    lottieDrawable.reverseAnimation();
  }

  @SuppressWarnings("unused") public void setSpeed(float speed) {
    lottieDrawable.setSpeed(speed);
  }

  public void cancelAnimation() {
    lottieDrawable.cancelAnimation();
  }

  public void pauseAnimation() {
    float progress = getProgress();
    lottieDrawable.cancelAnimation();
    setProgress(progress);
  }

  public void setProgress(@FloatRange(from = 0f, to = 1f) float progress) {
    lottieDrawable.setProgress(progress);
  }

 
}
```



![1]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/lottie/01.png
![2]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/lottie/02.png
![3]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/lottie/03.png
# Android - 签名机制

## 一、什么是签名？

要想知道签名是什么，先来看为什么需要签名 ？

了解 HTTPS 通信的同学应该知道，在消息通信时，必须至少解决两个问题：一是确保消息来源的真实性，二是确保消息不会被第三方篡改。在安装 APK 时，同样需要确保 APK 来源的真实性，以及 APK 没有被第三方篡改。如何解决这两个问题呢？方法就是开发者对 APK 进行签名：在 APK 中写入一个“指纹”。指纹写入以后，APK 中有任何修改，都会导致这个指纹无效，Android 系统在安装 APK 进行签名校验时就会不通过，从而保证了安全性。

要了解如何实现签名，需要了解两个基本概念：消息摘要、数字签名和数字证书。

### 1.1 消息摘要（Message Digest）

消息摘要（Message Digest），又称数字摘要（Digital Digest）或数字指纹（Finger Print）。简单来说，消息摘要就是在消息数据上，执行一个单向的 Hash 函数，生成一个固定长度的Hash值，这个Hash值即是消息摘要。

上面提到的的加密 Hash 函数就是消息摘要算法。它有以下特征：

- 无论输入的消息有多长，计算出来的消息摘要的长度总是固定的。

  > 例如：应用 MD5 算法摘要的消息有128个比特位，用 SHA-1 算法摘要的消息最终有 160 比特位的输出，SHA-1 的变体可以产生 192 比特位和 256 比特位的消息摘要。一般认为，摘要的最终输出越长，该摘要算法就越安全。

- 消息摘要看起来是“随机的”。

  > 这些比特看上去是胡乱的杂凑在一起的。可以用大量的输入来检验其输出是否相同，一般，不同的输入会有不同的输出，而且输出的摘要消息可以通过随机性检验。但是，一个摘要并不是真正随机的，因为用相同的算法对相同的消息求两次摘要，其结果必然相同；而若是真正随机的，则无论如何都是无法重现的。因此消息摘要是“伪随机的”。

- 消息摘要函数是单向函数，即只能进行正向的信息摘要，而无法从摘要中恢复出任何的消息，甚至根本就找不到任何与原信息相关的信息。

  > 当然，可以采用强力攻击的方法，即尝试每一个可能的信息，计算其摘要，看看是否与已有的摘要相同，如果这样做，最终肯定会恢复出摘要的消息。但实际上，要得到的信息可能是无穷个消息之一，所以这种强力攻击几乎是无效的。

- 好的摘要算法，没有人能从中找到“碰撞”。或者说，无法找到两条消息，使它们的摘要相同。

  > 虽然“碰撞”是肯定存在的（由于长明文生成短摘要的Hash必然会产生碰撞）。即对于给定的一个摘要，不可能找到一条信息使其摘要正好是给定的。

正是由于以上特点，消息摘要算法被广泛应用在“数字签名”领域，作为对明文的摘要算法。著名的消息摘要算法有 RSA 公司的 MD5 算法和 SHA-1 算法及其大量的变体。

> SHA-256 是 SHA-1 的升级版，现在 Android 签名使用的默认算法都已经升级到 SHA-256 了。

消息摘要的这种特性，很适合来验证数据的完整性。比如：在网络传输过程中下载一个大文件 BigFile，我们会同时从网络下载 BigFile 和 BigFile.md5，BigFile.md5 保存 BigFile 的摘要，我们在本地生成 BigFile 的消息摘要和 BigFile.md5 比较，如果内容相同，则表示下载过程正确。

> 注意，消息摘要只能保证消息的完整性，并不能保证消息的不可篡改性。

### 1.2 数字签名（Digital Signature）

数字签名方案是一种以电子形式存储消息签名的方法。一个完整的数字签名方案应该由两部分组成：签名算法和验证算法。在讲数字签名之前，我们先简单介绍几个相关知识点：“公钥密码体制”、“对称加密算法”、“非对称加密算法”。

#### 1.2.1 公钥密码体制（public-key cryptography）

公钥密码体制分为三个部分，公钥、私钥、加密解密算法，它的加密解密过程如下：

- 加密：通过加密算法和公钥对内容（或者说明文）进行加密，得到密文。加密过程需要用到公钥。
- 解密：通过解密算法和私钥对密文进行解密，得到明文。解密过程需要用到解密算法和私钥。注意，由公钥加密的内容，只能由私钥进行解密，也就是说，由公钥加密的内容，如果不知道私钥，是无法解密的。

公钥密码体制的公钥和算法都是公开的(这是为什么叫公钥密码体制的原因)，私钥是保密的。大家都以使用公钥进行加密，但是只有私钥的持有者才能解密。在实际 的使用中，有需要的人会生成一对公钥和私钥，把公钥发布出去给别人使用，自己保留私钥。目前使用最广泛的公钥密码体制是RSA密码体制。

#### 1.2.2 对称加密算法（symmetric key algorithms）

在对称加密算法中，加密和解密都是使用的同一个密钥。因此对称加密算法要保证安全性的话，密钥要做好保密，只能让使用的人知道，不能对外公开。

#### 1.2.3 非对称加密算法（asymmetric key algorithms）

在非对称加密算法中，加密使用的密钥和解密使用的密钥是不相同的。前面所说的公钥密码体制就是一种非对称加密算法，它的公钥和是私钥是不能相同的，也就是说加密使用的密钥和解密使用的密钥不同，因此它是一个非对称加密算法。

#### 1.2.4 RSA 简介

RSA 密码体制是一种公钥密码体制，公钥公开，私钥保密，它的加密解密算法是公开的。 由公钥加密的内容可以并且只能由私钥进行解密，而由私钥加密的内容可以并且只能由公钥进行解密。也就是说，RSA 的这一对公钥、私钥都可以用来加密和解密，并且一方加密的内容可以由并且只能由对方进行解密。

- 加密：公钥加密，私钥解密的过程，称为“加密”。因为公钥是公开的，任何公钥持有者都可以将想要发送给私钥持有者的信息进行加密后发送，而这个信息只有私钥持有者才能解密。
- 签名： 私钥加密，公钥解密的过程，称为“签名”。它和加密有什么区别呢？因为公钥是公开的，所以任何持有公钥的人都能解密私钥加密过的密文，所以这个过程并不能保证消息的安全性，但是它却能保证消息来源的准确性和不可否认性，也就是说，如果使用公钥能正常解密某一个密文，那么就能证明这段密文一定是由私钥持有者发布的，而不是其他第三方发布的，并且私钥持有者不能否认他曾经发布过该消息。故此将该过程称为“签名”。

#### 1.2.5 数字签名

事实上，任何一个公钥密码体制都可以单独地作为一种数字签名方案使用。如RSA作为数字签名方案使用时，可以定义如下：

> 这种签名实际上就是用信源的私钥加密消息，加密后的消息即成了签体；而用对应的公钥进行验证，若公钥解密后的消息与原来的消息相同，则消息是完整的，否则消息不完整。
>
> 它正好和公钥密码用于消息保密是相反的过程。因为只有信源才拥有自己地私钥，别人无法重新加密源消息，所以即使有人截获且更改了源消息，也无法重新生成签体，因为只有用信源的私钥才能形成正确地签体。
>
> 同样信宿只要验证用信源的公钥解密的消息是否与明文消息相同，就可以知道消息是否被更改过，而且可以认证消息是否是确实来自意定的信源，还可以使信源不能否认曾经发送的消息。所以 这样可以完成数字签名的功能。

但这种方案过于单纯，它仅可以保证消息的完整性，而无法确保消息的保密性。而且这种方案要对所有的消息进行加密操作，这在消息的长度比较大时，效率是非常低的，主要原因在于公钥体制的加解密过程的低效性。所以这种方案一般不可取。

几乎所有的数字签名方案都要和快速高效的摘要算法（Hash函数）一起使用，当公钥算法与摘要算法结合起来使用时，便构成了一种有效地数字签名方案。

这个过程是：

- 用摘要算法对消息进行摘要。
- 再把摘要值用信源的私钥加密。

通过以上两步得到的消息就是所谓的原始信息的数字签名，发送者需要将原始信息和数字签名一同发送给接收者。而接收者在接收到原始信息和数字签名后，通过以下 3 步验证消息的真伪：

1. 先把接收到的原始消息用同样的摘要算法摘要，形成“准签体”。

2. 对附加上的那段数字签名，使用预先得到的公钥解密。

3. 比较前两步所得到的两段消息是否一致。如果一致，则表明消息确实是期望的发送者发的，且内容没有被篡改过；相反，如果不一致，则表明传送的过程中一定出了问题，消息不可信。

这种方法使公钥加密只对消息摘要进行操作，因为一种摘要算法的摘要消息长度是固定的，而且都比较“短”（相对于消息而言），正好符合公钥加密的要求。这样效率得到了提高，而其安全性也并未因为使用摘要算法而减弱。

综上所述，数字签名是非对称加密技术 + 消息摘要技术的结合。

### 1.3 数字证书（Digital Certificate）

通过数字签名技术，确实可以解决可靠通信的问题。一旦验签通过，接收者就能确信该消息是期望的发送者发送的，而发送者也不能否认曾经发送过该消息。

大家有没有注意到，前面讲的数字签名方法，有一个前提，就是消息的接收者必须事先得到正确的公钥。如果一开始公钥就被别人篡改了，那坏人就会被你当成好人，而真正的消息发送者给你发的消息会被你视作无效的。而且，很多时候根本就不具备事先沟通公钥的信息通道。

那么如何保证公钥的安全可信呢？这就要靠数字证书来解决了。

数字证书是一个经证书授权（Certificate Authentication）中心数字签名的包含公钥拥有者信息以及公钥的文件。数字证书的格式普遍采用的是 X.509 V3 国际标准，一个标准的 X.509 数字证书通常包含以下内容：

- 证书的发布机构（Issuer）

  > 该证书是由哪个机构（CA中心）颁发的。

- 证书的有效期（Validity）

  > 证书的有效期，或者说使用期限。过了该日期，证书就失效了。

- 证书所有人的公钥（Public-Key）

  > 该证书所有人想要公布出去的公钥。

- 证书所有人的名称（Subject）

  > 这个证书是发给谁的，或者说证书的所有者，一般是某个人或者某个公司名称、机构的名称、公司网站的网址等。

- 证书所使用的签名算法（Signature algorithm）

  > 这个数字证书的数字签名所使用的加密算法，这样就可以使用证书发布机构的证书里面的公钥，根据这个算法对指纹进行解密。

- 证书发行者对证书的数字签名（Thumbprint） 

  > 也就是该数字证书的指纹，用于保证数字证书的完整性，确保证书没有被修改过。其原理就是在发布证书时，CA机构会根据签名算法（Signature algorithm）对整个证书计算其hash值（指纹）并和证书放在一起，使用者打开证书时，自己也根据签名算法计算一下证书的hash值（指纹），如 果和证书中记录的指纹对的上，就说明证书没有被修改过。

可以看出，数字证书本身也用到了数字签名技术，只不过签名的内容是整个证书（里面包含了证书所有者的公钥以及其他一些内容）。与普通数字签名不同的是，数字证书的签名者不是随随便便一个普通机构，而是 CA 机构。这就好像你的大学毕业证书上签名的一般都是德高望重的校长一样。一般来说，这些 CA 机构的根证书已经在设备出厂前预先安装到了你的设备上了。所以，数字证书可以保证证书里的公钥确实是这个证书所有者的，或者证书可以用来确认对方的身份。可见，数字证书主要是用来解决公钥的安全发放问题。

综上所述，总结一下，数字签名和签名验证的大体流程如下图所示：

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/01.png)

## 二、APK Signature Scheme v1

### 2.1 签名工具

Android 应用的签名工具有两种：`jarsigner` 和 `signAPK`。它们的签名算法没什么区别，主要是签名使用的文件不同。

- jarsigner：jdk 自带的签名工具，可以对 jar 进行签名。使用 keystore 文件进行签名。生成的签名文件默认使用 keystore 的别名命名。
- signAPK：Android sdk 提供的专门用于 Android 应用的签名工具。使用 pk8、x509.pem 文件进行签名。其中 pk8 是私钥文件，x509.pem 是含有公钥的文件。生成的签名文件统一使用“CERT”命名。

既然这两个工具都是给 APK 签名的，那么 keystore 文件和 pk8，x509.pem 他们之间是不是有什么联系呢？答案是肯定的，他们之间是可以转化的，这里就不再分析如何进行转化，网上的例子很多。

还有一个需要注意的知识点，如果我们查看一个keystore 文件的内容，会发现里面包含有一个 MD5 和 SHA1 摘要，这个就是 keystore 文件中私钥的数据摘要，这个信息也是我们在申请很多开发平台账号时需要填入的信息。

### 2.2 签名过程

首先我们任意选取一个签名后的 APK（Sample-release.APK）解压：

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/02.png)

在 `META-INF` 文件夹下有三个文件：`MANIFEST.MF`、`CERT.SF`、`CERT.RSA`。它们就是签名过程中生成的文件，姑且叫他们“签名三兄弟”吧，把它们搞清楚了，你就精通签名了。

#### 2.2.1 MANIFEST.MF

该文件中保存的内容其实就是逐一遍历 APK 中的所有条目，如果是目录就跳过，如果是一个文件，就用 SHA1（或者 SHA256）消息摘要算法提取出该文件的摘要然后进行 BASE64 编码后，作为“SHA1-Digest”属性的值写入到 MANIFEST.MF 文件中的一个块中。该块有一个“Name”属性， 其值就是该文件在 APK 包中的路径。

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/03.png)

#### 2.2.2 CERT.SF

- SHA1-Digest-Manifest-Main-Attributes：对 MANIFEST.MF 头部的块做 SHA1（或者SHA256）后再用 Base64 编码

- SHA1-Digest-Manifest：对整个 MANIFEST.MF 文件做 SHA1（或者 SHA256）后再用 Base64 编码

- SHA1-Digest：对 MANIFEST.MF 的各个条目做 SHA1（或者 SHA256）后再用 Base64 编码

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/04.png)

对于 SHA1-Digest 值的验证可以手动进行，将 MANIFEST.MF 中任意一个块的内容复制并保存在一个新的文档中，注意文末需要加两个换行（这是由 signAPK 的源码决定的）

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/05.png)

#### 2.2.3 CERT.RSA

这里会把之前生成的 CERT.SF 文件，用私钥计算出签名, 然后将签名以及包含公钥信息的数字证书一同写入 CERT.RSA 中保存。这里要注意的是，Android APK 中的 CERT.RSA 证书是自签名的，并不需要这个证书是第三方权威机构发布或者认证的，用户可以在本地机器自行生成这个自签名证书。Android 目前不对应用证书进行 CA 认证。

##### 2.2.3.1 什么是自签名证书？

所谓自签名证书是指自己给自己颁发的证书，即公钥证书中 Issuer（发布者）和 Subject（所有者）是相同的。当然，APK 也可以采用由 CA 颁发私钥证书进行签名。采用非自签名时，最终 APK 的公钥证书中就会包含证书链，并且会存在多余一个证书，证书间通过 Issuer 与 Subject进行关联，Issuer 负责对 Subject 进行认证。当安装 APK 时，系统只会用位于证书链 中最底层的证书对 APK 进行校验，但并不会验证证书链的有效性。

在 HTTPS 通信中使用自签名证书时浏览器的显示效果：

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/06.png)

CERT.RSA 文件中的内容：

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/07.png)

这里我们看到的都是二进制文件，因为RSA文件加密了，所以我们需要用openssl命令才能查看其内容：

> $ openssl pkcs7 -inform DER -in /<文件存放路径>/Sample-release_new/original/META-INF/CERT.RSA -text -noout -print_certs

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/08.png)

综上所述，一个完整的签名过程如下所示：

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/09.png)

### 2.3 签名校验过程

签名验证是发生在APK的安装过程中，一共分为三步：

1. 检查 APK 中包含的所有文件，对应的摘要值与 MANIFEST.MF 文件中记录的值一致。

2. 使用证书文件（RSA 文件）检验签名文件（SF 文件）没有被修改过。

3. 使用签名文件（SF 文件）检验 MF 文件没有被修改过。

综上所述，一个完整的签名验证过程如下所示：

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/10.png)

为什么使用这样的签名流程呢？

我们假设一下，首先，如果你改变了 APK 包中的任何文件，那么在 APK 安装校验时，改变后的文件摘要信息与 MANIFEST.MF 的检验信息不同，于是验证失败，程序就不能成功安装。

其次，如果你对更改过的文件相应的算出新的摘要值，然后更改 MANIFEST.MF 文件里面对应的属性值，那么必定与 CERT.SF 文件中算出的摘要值不一样，照样验证失败。

最后，如果你还不死心，继续计算 MANIFEST.MF 的摘要值，相应的更改 CERT.SF 里面的值，那么数字签名值必定与 CERT.RSA 文件中记录的不一样，还是失败。

那么能不能继续伪造数字签名呢？不可能，因为没有数字证书对应的私钥。

## 三、APK Signature Scheme v2

APK 签名方案 v2 是一种全文件签名方案，该方案能够发现对 APK 的受保护部分进行的所有更改，从而有助于加快验证速度并增强完整性保证。

### 3.1 v1 签名机制的劣势

从 Android 7.0 开始，Android 支持了一套全新的 V2 签名机制，为什么要推出新的签名机制呢？通过前面的分析，可以发现 v1 签名有两个地方可以改进：

- 签名校验速度慢

校验过程中需要对apk中所有文件进行摘要计算，在 APK 资源很多、性能较差的机器上签名校验会花费较长时间，导致安装速度慢。

- 完整性保障不够

META-INF 目录用来存放签名，自然此目录本身是不计入签名校验过程的，可以随意在这个目录中添加文件，比如一些快速批量打包方案就选择在这个目录中添加渠道文件。

为了解决这两个问题，在 Android 7.0 Nougat 中引入了全新的 APK Signature Scheme v2。

### 3.2 v2 带来了什么变化？

由于在 v1 仅针对单个 ZIP 条目进行验证，因此，在 APK 签署后可进行许多修改 — 可以移动甚至重新压缩文件。事实上，编译过程中要用到的 ZIPalign 工具就是这么做的，它用于根据正确的字节限制调整 ZIP 条目，以改进运行时性能。而且我们也可以利用这个东西，在打包之后修改 META-INF 目录下面的内容，或者修改 ZIP 的注释来实现多渠道的打包，在 v1 签名中都可以校验通过。

v2 签名将验证归档中的所有字节，而不是单个 ZIP 条目，因此，在签署后无法再运行 ZIPalign（必须在签名之前执行）。正因如此，现在，在编译过程中，Google 将压缩、调整和签署合并成一步完成。

### 3.3 v2 签名模式

简单来说，v2 签名模式在原先 APK 块中增加了一个新的块（签名块），新的块存储了签名，摘要，签名算法，证书链，额外属性等信息，这个块有特定的格式，具体格式分析见后文，先看下现在 APK 成什么样子了。

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/11.png)

为了保护 APK 内容，整个 APK（ZIP文件格式）被分为以下 4 个区块：

- ZIP 条目的内容（从偏移量 0 处开始一直到“APK 签名分块”的起始位置）
- APK 签名分块
- ZIP 中央目录
- ZIP 中央目录结尾

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/12.png)

其中，应用签名方案的签名信息会被保存在 区块 2（APK Signing Block）中，而区块 1（Contents of ZIP entries）、区块 3（ZIP Central Directory）、区块 4（ZIP End of Central Directory）是受保护的，在签名后任何对区块 1、3、4 的修改都逃不过新的应用签名方案的检查。

### 3.4 签名过程

从上面我们可以看到 v2 模式块有点类似于我们 `META-INF` 文件夹下的信息内容。那么对于上述当中摘要的信息又是怎么计算出来的呢。

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/13.png)

首先，说一下 APK 摘要计算规则，对于每个摘要算法，计算结果如下:

- 将 APK 中文件 ZIP 条目的内容、ZIP 中央目录、ZIP 中央目录结尾按照 1MB 大小分割成一些小块。
- 计算每个小块的数据摘要，数据内容是 0xa5 + 块字节长度 + 块内容。
- 计算整体的数据摘要，数据内容是 0x5a + 数据块的数量 + 每个数据块的摘要内容

总之，就是把 APK 按照 1M 大小分割，分别计算这些分段的摘要，最后把这些分段的摘要在进行计算得到最终的摘要也就是 APK 的摘要。然后将 APK 的摘要 + 数字证书 + 其他属性生成签名数据写入到 APK Signing Block 区块。

### 3.5 签名校验过程

接下来我们来看v2签名的校验过程，整体大概流程如下图所示：

![](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android_sign/14.png)

其中 v2 签名机制是在 Android 7.0 以及以上版本才支持。因此对于 Android 7.0 以及以上版本，在安装过程中，如果发现有 v2 签名块，则必须走 v2 签名机制，不能绕过。否则降级走 v1 签名机制。
v1 和 v2 签名机制是可以同时存在的，其中对于 v1 和 v2 版本同时存在的时候，v1 版本的 META_INF 的 `.SF` 文件属性当中有一个 `X-Android-APK-Signed` 属性：

```
X-Android-APK-Signed: 2
```

因此如果想绕过 v2 走 v1 校验是不行的。

### 3.6 v2 对多渠道打包的影响

之前的渠道包生成方案是通过在 META-INF 目录下添加空文件，用空文件的名称来作为渠道的唯一标识。但在新的应用签名方案下 META-INF 已经被列入了保护区了，向 META-INF 添加空文件的方案会对区块 1、3、4 都会有影响。

可以参考：[美团解决方案](https://github.com/Meituan-Dianping/walle)。

## 参考资料

- [APK 签名方案 v2](https://source.android.com/security/apksigning/v2)
- [分析Android V2新签名打包机制](https://mp.weixin.qq.com/s?__biz=MzI1NjEwMTM4OA==&mid=2651232457&idx=1&sn=90b16c3868a341272b8f1aa26d6c0122&chksm=f1d9e5aac6ae6cbcfaecb07bdd280abf81a46f1937c43f61e69d7f78d64350943356f5443d58&scene=27#wechat_redirect)
- [3个知识点让你了解Android签名机制](https://www.apkbus.com/blog-942559-76948.html)
- [新一代开源Android渠道包生成工具Walle](https://tech.meituan.com/android_apk_v2-signature_scheme.html)
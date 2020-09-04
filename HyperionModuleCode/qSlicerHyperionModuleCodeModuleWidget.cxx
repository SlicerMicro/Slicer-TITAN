/*==============================================================================

  Program: 3D Slicer

  Portions (c) Copyright Brigham and Women's Hospital (BWH) All Rights Reserved.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

==============================================================================*/

// Qt includes
#include <QDebug>

// Slicer includes
#include "qSlicerHyperionModuleCodeModuleWidget.h"
#include "ui_qSlicerHyperionModuleCodeModuleWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerHyperionModuleCodeModuleWidgetPrivate: public Ui_qSlicerHyperionModuleCodeModuleWidget
{
public:
  qSlicerHyperionModuleCodeModuleWidgetPrivate();
};

//-----------------------------------------------------------------------------
// qSlicerHyperionModuleCodeModuleWidgetPrivate methods

//-----------------------------------------------------------------------------
qSlicerHyperionModuleCodeModuleWidgetPrivate::qSlicerHyperionModuleCodeModuleWidgetPrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerHyperionModuleCodeModuleWidget methods

//-----------------------------------------------------------------------------
qSlicerHyperionModuleCodeModuleWidget::qSlicerHyperionModuleCodeModuleWidget(QWidget* _parent)
  : Superclass( _parent )
  , d_ptr( new qSlicerHyperionModuleCodeModuleWidgetPrivate )
{
}

//-----------------------------------------------------------------------------
qSlicerHyperionModuleCodeModuleWidget::~qSlicerHyperionModuleCodeModuleWidget()
{
}

//-----------------------------------------------------------------------------
void qSlicerHyperionModuleCodeModuleWidget::setup()
{
  Q_D(qSlicerHyperionModuleCodeModuleWidget);
  d->setupUi(this);
  this->Superclass::setup();
}
